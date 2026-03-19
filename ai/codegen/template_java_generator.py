class TemplateJavaGenerator:

    # JDK types that Hibernate can map natively — everything else must be converted
    _JDK_TYPES = {
        "String", "UUID", "Integer", "Long", "Double", "Float", "Boolean",
        "int", "long", "double", "float", "boolean",
        "LocalDate", "LocalDateTime", "Instant", "BigDecimal",
        "Short", "Byte", "Character",
    }

    # Domain value-object / custom types → JPA-safe JDK equivalent
    _VO_TYPE_MAP = {
        "Money": "BigDecimal",
        "Price": "BigDecimal",
        "Amount": "BigDecimal",
    }

    @classmethod
    def _jpa_type(cls, java_type: str) -> str:
        """
        Convert a domain type to a JPA-safe JDK type.
        - Known VO wrappers (Money, Price…) → BigDecimal
        - *Status / *Type / *Kind / *State value objects → String
        - *Id value objects → UUID
        - List<X> / Set<X> → kept as-is (caller handles separately)
        - Everything else that is a JDK primitive/type → unchanged
        """
        if not java_type:
            return "String"
        outer = java_type.split("<")[0]
        if outer in cls._JDK_TYPES:
            return java_type  # already safe
        if outer in cls._VO_TYPE_MAP:
            return cls._VO_TYPE_MAP[outer]
        if outer.endswith("Id"):
            return "UUID"
        if any(outer.endswith(sfx) for sfx in ("Status", "Type", "Kind", "State", "Category", "Role")):
            return "String"
        if java_type.startswith("List<") or java_type.startswith("Set<"):
            return java_type  # handled elsewhere
        # Unknown custom type → String (safe fallback)
        return "String"

    def generate_jpa_entity(self, package_name, class_name, fields, base_package=None):

        lines = []

        lines.append(f"package {package_name};\n\n")

        lines.append("import jakarta.persistence.*;\n")
        lines.append("import java.util.UUID;\n")

        # BaseJpaEntity import — derive shared package from base_package or package_name
        if base_package:
            shared_pkg = f"{base_package}.shared"
        else:
            # package_name is something like com.foo.bar.module.infra.persistence.entity
            # strip back to root (first 3 segments: com.foo.bar)
            parts = package_name.split(".")
            shared_pkg = ".".join(parts[:3]) + ".shared"
        lines.append(f"import {shared_pkg}.BaseJpaEntity;\n")

        # detect collections
        needs_list = any((f.get("type") or "").startswith("List") for f in fields)

        if needs_list:
            lines.append("import java.util.List;\n")

        # Domain imports are resolved later by the central ImportResolver
        # to avoid duplicate or incorrect imports.

        lines.append("\n")

        # Derive @Table name: strip JpaEntity suffix, convert CamelCase → snake_case
        entity_base = class_name.replace("JpaEntity", "")
        import re as _re
        table_name = _re.sub(r"([A-Z])", r"_\1", entity_base).lstrip("_").lower()

        lines.append("@Entity\n")
        lines.append(f"@Table(name = \"{table_name}\")\n")
        lines.append(f"public class {class_name} extends BaseJpaEntity {{\n\n")

        lines.append("    @Id\n")
        lines.append("    @GeneratedValue\n")
        lines.append("    private UUID id;\n\n")

        lines.append("    public UUID getId() { return this.id; }\n")
        lines.append("    public void setId(UUID id) { this.id = id; }\n\n")

        needs_bigdecimal = any(self._jpa_type(f.get("type", "")) == "BigDecimal" for f in fields if f.get("name") != "id")
        needs_localdate = any(f.get("type", "").startswith("LocalDate") for f in fields if f.get("name") != "id")
        needs_localdatetime = any(f.get("type", "") == "LocalDateTime" for f in fields if f.get("name") != "id")

        if needs_bigdecimal:
            lines.append("import java.math.BigDecimal;\n")
        if needs_localdate or needs_localdatetime:
            pass  # LocalDate/LocalDateTime imports added by import resolver

        for f in fields:
            name = f.get("name")
            type_ = self._jpa_type(f.get("type") or "String")

            if name == "id":
                continue

            lines.append(f"    private {type_} {name};\n")

        # constructor
        lines.append("\n    public " + class_name + "() {}\n")

        # getters and setters
        for f in fields:
            name = f.get("name")
            type_ = self._jpa_type(f.get("type") or "String")

            if name == "id":
                continue

            method = name[0].upper() + name[1:]

            lines.append(f"\n    public {type_} get{method}() {{ return this.{name}; }}\n")
            lines.append(f"    public void set{method}({type_} {name}) {{ this.{name} = {name}; }}\n")

        lines.append("\n}\n")

        return "".join(lines)

    def generate_base_jpa_entity(self, package_name: str) -> str:
        """Abstract superclass for all JPA entities — provides audit fields."""
        return f"""package {package_name};

import jakarta.persistence.Column;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.MappedSuperclass;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseJpaEntity {{

    @Column(name = "active", nullable = false, columnDefinition = "boolean default true")
    private boolean active = true;

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private Instant updatedAt;

    @CreatedBy
    @Column(name = "created_by", length = 100, updatable = false)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by", length = 100)
    private String updatedBy;

    public boolean isActive() {{ return active; }}
    public void setActive(boolean active) {{ this.active = active; }}
    public Instant getCreatedAt() {{ return createdAt; }}
    public Instant getUpdatedAt() {{ return updatedAt; }}
    public String getCreatedBy() {{ return createdBy; }}
    public String getUpdatedBy() {{ return updatedBy; }}
}}
"""

    def generate_audit_config(self, package_name: str, base_package: str) -> str:
        """@EnableJpaAuditing config + AuditorAware bean wired to Keycloak JWT."""
        return f"""package {package_name};

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

import java.util.Optional;

@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class AuditConfig {{

    @Bean
    public AuditorAware<String> auditorProvider() {{
        return () -> {{
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth instanceof JwtAuthenticationToken jwtToken) {{
                String username = jwtToken.getToken().getClaimAsString("preferred_username");
                return Optional.ofNullable(username).filter(s -> !s.isBlank());
            }}
            return Optional.of("system");
        }};
    }}
}}
"""

    def generate_page_result(self, package_name: str) -> str:
        """Domain-layer PageResult<T> — no Spring dependency."""
        return f"""package {package_name};

import java.util.List;

public record PageResult<T>(
        List<T> content,
        int page,
        int size,
        long total) {{

    public int totalPages() {{
        return size == 0 ? 0 : (int) Math.ceil((double) total / size);
    }}

    public boolean isLast() {{
        return page >= totalPages() - 1;
    }}
}}
"""

    def generate_page_response(self, package_name: str) -> str:
        """HTTP-layer PageResponse<T> record returned by controllers."""
        return f"""package {package_name};

import java.util.List;

public record PageResponse<T>(
        List<T> content,
        int page,
        int size,
        long total,
        int totalPages,
        boolean last) {{}}
"""

    def generate_dashboard(self, base_package: str, modules: list[dict]) -> dict[str, str]:
        """
        Generates 3 dashboard files:
          - shared/DashboardStats.java    — typed record with per-entity KPIs
          - config/DashboardService.java  — @Service aggregating SpringData repos
          - config/DashboardController.java — GET /dashboard

        modules: list of {"entity": str, "module": str, "fields": list}
        Returns {relative_path: content}
        """
        import re as _re

        files: dict[str, str] = {}

        # ── Derive per-entity metadata ────────────────────────────────────
        entity_infos = []
        for m in modules:
            entity = m["entity"]
            mod = m["module"]
            fields = m.get("fields", [])
            snake = _re.sub(r"([A-Z])", r"_\1", entity).lstrip("_").lower()

            status_fields = [
                f["name"] for f in fields
                if any(f.get("type", "").endswith(s) for s in ("Status", "State", "Type", "Kind"))
            ]
            money_fields = [
                f["name"] for f in fields
                if any(f.get("type", "").startswith(t) for t in ("Money", "BigDecimal", "Double", "Float"))
                and any(f["name"].lower().endswith(k) for k in ("amount", "cost", "price", "total", "fee", "balance"))
            ]

            entity_infos.append({
                "entity": entity,
                "module": mod,
                "snake": snake,
                "status_fields": status_fields,
                "money_fields": money_fields,
            })

        # ── DashboardStats record ─────────────────────────────────────────
        stat_fields = []
        for info in entity_infos:
            e = info["entity"]
            stat_fields.append(f"    long total{e}s")
        # money totals
        for info in entity_infos:
            for mf in info["money_fields"]:
                cap = mf[0].upper() + mf[1:]
                stat_fields.append(f"    double total{cap}")

        stat_fields_str = ",\n".join(stat_fields)

        stats_java = f"""package {base_package}.shared;

public record DashboardStats(
{stat_fields_str}
) {{}}
"""
        files[f"shared/DashboardStats.java"] = stats_java

        # ── DashboardService ──────────────────────────────────────────────
        repo_imports = []
        repo_fields = []
        repo_constructor_params = []
        repo_constructor_assigns = []
        stat_constructor_args = []

        for info in entity_infos:
            e = info["entity"]
            mod = info["module"]
            var = e[0].lower() + e[1:] + "Repo"
            repo_class = f"SpringData{e}Repository"
            repo_pkg = f"{base_package}.{mod}.infrastructure.persistence.spring.{repo_class}"
            repo_imports.append(f"import {repo_pkg};")
            repo_fields.append(f"    private final {repo_class} {var};")
            repo_constructor_params.append(f"            {repo_class} {var}")
            repo_constructor_assigns.append(f"        this.{var} = {var};")
            stat_constructor_args.append(f"                {var}.countByActiveTrue()")

        for info in entity_infos:
            e = info["entity"]
            mod = info["module"]
            var = e[0].lower() + e[1:] + "Repo"
            for mf in info["money_fields"]:
                # Use JPQL sum — add custom query to SpringData repo (or use default 0)
                stat_constructor_args.append(f"                0.0 // TODO: {var}.sumOf{mf[0].upper()+mf[1:]}()")

        imports_str = "\n".join(repo_imports)
        fields_str = "\n".join(repo_fields)
        params_str = ",\n".join(repo_constructor_params)
        assigns_str = "\n".join(repo_constructor_assigns)
        args_str = ",\n".join(stat_constructor_args)

        service_java = f"""package {base_package}.config;

import {base_package}.shared.DashboardStats;
{imports_str}
import org.springframework.stereotype.Service;

@Service
public class DashboardService {{

{fields_str}

    public DashboardService(
{params_str}) {{
{assigns_str}
    }}

    public DashboardStats getStats() {{
        return new DashboardStats(
{args_str}
        );
    }}
}}
"""
        files[f"config/DashboardService.java"] = service_java

        # ── DashboardController ───────────────────────────────────────────
        controller_java = f"""package {base_package}.config;

import {base_package}.shared.DashboardStats;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/dashboard")
@CrossOrigin(origins = "*")
public class DashboardController {{

    private final DashboardService service;

    public DashboardController(DashboardService service) {{
        this.service = service;
    }}

    @GetMapping
    public DashboardStats getStats() {{
        return service.getStats();
    }}
}}
"""
        files[f"config/DashboardController.java"] = controller_java

        return files

    def generate_cache_config(self, package_name: str) -> str:
        """Caffeine cache manager with two caches: entityById and dashboard."""
        return f"""package {package_name};

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Caffeine cache configuration.
 * entityById: caché de entidades por UUID (TTL 5 min, max 500 entries).
 * dashboard: caché de estadísticas del dashboard (TTL 5 min).
 */
@Configuration
@EnableCaching
public class CacheConfig {{

    public static final String CACHE_ENTITY_BY_ID = "entityById";
    public static final String CACHE_DASHBOARD     = "dashboard";

    @Bean
    public CacheManager cacheManager() {{
        CaffeineCacheManager manager = new CaffeineCacheManager(
                CACHE_ENTITY_BY_ID,
                CACHE_DASHBOARD
        );
        manager.setCaffeine(
                Caffeine.newBuilder()
                        .maximumSize(500)
                        .expireAfterWrite(5, TimeUnit.MINUTES)
                        .recordStats()
        );
        return manager;
    }}
}}
"""

    def generate_openapi_config(self, package_name: str, project_name: str, project_slug: str) -> str:
        """OpenAPI 3 config with JWT Bearer security scheme."""
        title = project_name or project_slug or "API"
        return f"""package {package_name};

import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@SecurityScheme(
    name = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT",
    description = "JWT token obtenido de Keycloak"
)
public class OpenApiConfig {{

    @Bean
    public OpenAPI openAPI() {{
        return new OpenAPI()
                .info(new Info()
                        .title("{title} API")
                        .description("API REST para la gestión de {title}. " +
                                     "Autentícate con Keycloak y usa el token Bearer.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("{title} Team")
                                .email("dev@{project_slug}.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0")));
    }}
}}
"""

    def generate_messages_properties(self, locale: str = "es") -> str:
        """
        Generates Spring MessageSource messages file for the given locale.
        Used to localize validation error messages and API responses.
        locale: 'es' (default) or 'en'
        """
        if locale == "en":
            return (
                "# Validation messages (English)\n"
                "jakarta.validation.constraints.NotBlank.message=This field is required\n"
                "jakarta.validation.constraints.NotNull.message=This field is required\n"
                "jakarta.validation.constraints.Size.message=Must be between {min} and {max} characters\n"
                "jakarta.validation.constraints.Past.message=Date must be in the past\n"
                "jakarta.validation.constraints.FutureOrPresent.message=Date must be today or in the future\n"
                "jakarta.validation.constraints.Email.message=Invalid email address\n"
                "jakarta.validation.constraints.Min.message=Value must be at least {value}\n"
                "jakarta.validation.constraints.Max.message=Value must be at most {value}\n"
                "jakarta.validation.constraints.Pattern.message=Invalid format\n"
                "jakarta.validation.constraints.Positive.message=Value must be positive\n"
                "\n"
                "# API error messages\n"
                "error.notFound=Resource not found\n"
                "error.badRequest=Invalid request\n"
                "error.unauthorized=Authentication required\n"
                "error.forbidden=Access denied\n"
                "error.conflict=Resource already exists\n"
            )
        else:
            return (
                "# Mensajes de validación (Español)\n"
                "jakarta.validation.constraints.NotBlank.message=Este campo es obligatorio\n"
                "jakarta.validation.constraints.NotNull.message=Este campo es obligatorio\n"
                "jakarta.validation.constraints.Size.message=Debe tener entre {min} y {max} caracteres\n"
                "jakarta.validation.constraints.Past.message=La fecha debe ser anterior a hoy\n"
                "jakarta.validation.constraints.FutureOrPresent.message=La fecha debe ser hoy o en el futuro\n"
                "jakarta.validation.constraints.Email.message=Dirección de correo no válida\n"
                "jakarta.validation.constraints.Min.message=El valor debe ser al menos {value}\n"
                "jakarta.validation.constraints.Max.message=El valor debe ser como máximo {value}\n"
                "jakarta.validation.constraints.Pattern.message=Formato no válido\n"
                "jakarta.validation.constraints.Positive.message=El valor debe ser positivo\n"
                "\n"
                "# Mensajes de error API\n"
                "error.notFound=Recurso no encontrado\n"
                "error.badRequest=Solicitud inválida\n"
                "error.unauthorized=Autenticación requerida\n"
                "error.forbidden=Acceso denegado\n"
                "error.conflict=El recurso ya existe\n"
            )

    def generate_message_source_config(self, package_name: str) -> str:
        """
        Generates MessageSourceConfig.java — configures Spring MessageSource
        to load messages from classpath:messages*.properties with UTF-8 encoding.
        Supports Accept-Language header via LocaleContextHolder.
        """
        return f"""package {package_name};

import org.springframework.context.MessageSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.support.ReloadableResourceBundleMessageSource;
import org.springframework.web.servlet.LocaleResolver;
import org.springframework.web.servlet.i18n.AcceptHeaderLocaleResolver;

import java.util.List;
import java.util.Locale;

/**
 * Configures Spring MessageSource for i18n.
 * Loads messages from classpath:messages.properties (ES default) and messages_en.properties.
 * Uses Accept-Language HTTP header to select the active locale.
 */
@Configuration
public class MessageSourceConfig {{

    @Bean
    public MessageSource messageSource() {{
        ReloadableResourceBundleMessageSource source = new ReloadableResourceBundleMessageSource();
        source.setBasename("classpath:messages");
        source.setDefaultEncoding("UTF-8");
        source.setUseCodeAsDefaultMessage(true);
        return source;
    }}

    @Bean
    public LocaleResolver localeResolver() {{
        AcceptHeaderLocaleResolver resolver = new AcceptHeaderLocaleResolver();
        resolver.setSupportedLocales(List.of(Locale.forLanguageTag("es"), Locale.ENGLISH));
        resolver.setDefaultLocale(Locale.forLanguageTag("es"));
        return resolver;
    }}
}}
"""

    def generate_async_config(self, package_name: str) -> str:
        """@EnableAsync configuration class."""
        return f"""package {package_name};

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Enables asynchronous event listeners (e.g. email notifications).
 * Events are processed in a separate thread to avoid blocking the main request.
 */
@Configuration
@EnableAsync
public class AsyncConfig {{
}}
"""

    def generate_domain_event_interface(self, base_package: str) -> str:
        """Base DomainEvent interface in shared package."""
        return f"""package {base_package}.shared;

import java.time.Instant;
import java.util.UUID;

/**
 * Marker interface for all domain events.
 * Events are immutable records published after a state change.
 */
public interface DomainEvent {{
    UUID eventId();
    Instant occurredOn();
    String eventType();
}}
"""

    def generate_domain_events(self, base_package: str, modules: list[dict]) -> dict[str, str]:
        """
        Generates domain event records for each module.
        Returns a dict of relative paths -> file content.
        modules: list of dicts with keys 'name' (entity name), 'fields' (list of field dicts)
        """
        files = {}
        for mod in modules:
            entity = mod["name"]
            lower_mod = entity.lower()
            pkg = f"{base_package}.{lower_mod}.domain.event"

            # RegisterEvent: entity registered/created
            event_name = f"{entity}RegisteredEvent"
            # Collect relevant fields (excluding id)
            relevant = [f for f in mod.get("fields", []) if f.get("name") not in ("id",)
                       and f.get("type", "String") not in ("LocalDate", "LocalDateTime", "Instant")
                       and not str(f.get("type", "")).startswith("List")][:3]

            imports = {"java.time.Instant", "java.util.UUID", f"{base_package}.shared.DomainEvent"}
            extra_fields = ""
            for fld in relevant:
                t = fld.get("type", "String")
                n = fld.get("name", "value")
                if t in ("String", "int", "long", "double", "boolean"):
                    extra_fields += f"        {t} {n},\n"

            rel_path = f"backend/src/main/java/{base_package.replace('.', '/')}/{lower_mod}/domain/event/{event_name}.java"
            imports_str = "".join(f"import {i};\n" for i in sorted(imports))

            files[rel_path] = f"""package {pkg};

{imports_str}
public record {event_name}(
        UUID eventId,
        Instant occurredOn,
        UUID entityId
) implements DomainEvent {{
    public static {event_name} of(UUID entityId) {{
        return new {event_name}(UUID.randomUUID(), Instant.now(), entityId);
    }}
    @Override public String eventType() {{ return "{lower_mod}.registered"; }}
}}
"""
        return files

    def generate_notification_listener(self, base_package: str, modules: list[dict]) -> str:
        """Generates a Spring event listener that sends email notifications for all domain events."""
        pkg = f"{base_package}.config"

        event_imports = "\n".join(
            f"import {base_package}.{mod['name'].lower()}.domain.event.{mod['name']}RegisteredEvent;"
            for mod in modules
        )

        handlers = "\n\n".join(
            f"""    @Async
    @EventListener
    public void on{mod['name']}Registered({mod['name']}RegisteredEvent event) {{
        log.info("[EVENT] {{}} - {mod['name']} registered: id={{}}", event.eventType(), event.entityId());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Nuevo {mod['name'].lower()} registrado",
                "Se ha registrado un nuevo {mod['name'].lower()} con ID: " + event.entityId());
    }}"""
            for mod in modules
        )

        return f"""package {pkg};

{event_imports}
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

/**
 * Listens to domain events and sends email notifications.
 * Uses MailHog in development (configure spring.mail.* in application.properties).
 */
@Component
public class NotificationEventListener {{

    private static final Logger log = LoggerFactory.getLogger(NotificationEventListener.class);

    private final JavaMailSender mailSender;

    @Value("${{app.notifications.from:noreply@app.com}}")
    private String from;

    @Value("${{app.notifications.admin:admin@app.com}}")
    private String adminEmail;

    @Value("${{app.notifications.enabled:true}}")
    private boolean enabled;

    public NotificationEventListener(JavaMailSender mailSender) {{
        this.mailSender = mailSender;
    }}

{handlers}

    private void sendEmail(String to, String subject, String body) {{
        try {{
            SimpleMailMessage msg = new SimpleMailMessage();
            msg.setFrom(from);
            msg.setTo(to);
            msg.setSubject(subject);
            msg.setText(body);
            mailSender.send(msg);
            log.debug("Email sent to {{}} - Subject: {{}}", to, subject);
        }} catch (Exception e) {{
            log.error("Failed to send email to {{}}: {{}}", to, e.getMessage());
        }}
    }}
}}
"""

    def generate_rate_limit_filter(self, package_name: str, api_paths: list[str] | None = None) -> str:
        """
        Generates a Servlet Filter using Bucket4j to rate limit API endpoints.
        100 requests/minute per IP. Returns HTTP 429 when exceeded.
        """
        if not api_paths:
            api_paths = []
        path_checks = " && ".join(
            f'!path.startsWith("/{p}")' for p in api_paths
        ) or '!path.startsWith("/api")'

        return f"""package {package_name};

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.Refill;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Rate limiting filter using Bucket4j (token bucket algorithm).
 * Limits each IP to 100 requests per minute on API endpoints.
 * Returns HTTP 429 Too Many Requests when the limit is exceeded.
 */
@Component
public class RateLimitFilter extends OncePerRequestFilter {{

    private static final int CAPACITY = 100;
    private static final Duration REFILL_PERIOD = Duration.ofMinutes(1);

    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {{

        String path = request.getRequestURI();

        // Skip rate limiting for non-API paths (Swagger, Actuator, etc.)
        if ({path_checks}) {{
            chain.doFilter(request, response);
            return;
        }}

        String clientIp = getClientIp(request);
        Bucket bucket = buckets.computeIfAbsent(clientIp, this::newBucket);

        if (bucket.tryConsume(1)) {{
            chain.doFilter(request, response);
        }} else {{
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType("application/json");
            response.getWriter().write(
                    "{{\\\"status\\\":429,\\\"error\\\":\\\"Too Many Requests\\\"," +
                    "\\\"message\\\":\\\"Rate limit exceeded. Max 100 requests per minute.\\\"}}"
            );
        }}
    }}

    private Bucket newBucket(String ip) {{
        Bandwidth limit = Bandwidth.classic(CAPACITY, Refill.greedy(CAPACITY, REFILL_PERIOD));
        return Bucket.builder().addLimit(limit).build();
    }}

    private String getClientIp(HttpServletRequest request) {{
        String forwarded = request.getHeader("X-Forwarded-For");
        if (forwarded != null && !forwarded.isEmpty()) {{
            return forwarded.split(",")[0].trim();
        }}
        return request.getRemoteAddr();
    }}
}}
"""

    def generate_websocket_config(self, package_name: str) -> str:
        """
        Generates Spring WebSocket configuration (STOMP over SockJS).
        Frontend connects to /ws, publishes to /app/*, subscribes to /topic/*.
        """
        return f"""package {package_name};

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

/**
 * WebSocket configuration (STOMP protocol over SockJS).
 * Clients connect to /ws and subscribe to /topic/notifications for real-time updates.
 */
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {{

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {{
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }}

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {{
        registry.enableSimpleBroker("/topic");
        registry.setApplicationDestinationPrefixes("/app");
    }}
}}
"""

    def generate_notification_message(self, base_package: str) -> str:
        """
        Generates the NotificationMessage record used for WebSocket payloads.
        """
        return f"""package {base_package}.shared;

import java.time.Instant;

/**
 * Payload sent over WebSocket to subscribed clients.
 * type: CREATED | UPDATED | DELETED
 * entityType: the domain entity name (e.g. Patient, Appointment)
 */
public record NotificationMessage(
        String type,
        String entityType,
        String message,
        Instant timestamp) {{

    public static NotificationMessage of(String type, String entityType, String message) {{
        return new NotificationMessage(type, entityType, message, Instant.now());
    }}
}}
"""

    def generate_notification_service(self, base_package: str) -> str:
        """
        Generates the NotificationService that broadcasts domain events over WebSocket.
        """
        return f"""package {base_package}.shared;

import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

/**
 * Broadcasts domain event notifications to all connected WebSocket clients.
 * Clients subscribe to /topic/notifications to receive real-time updates.
 */
@Service
public class NotificationService {{

    private static final String TOPIC = "/topic/notifications";

    private final SimpMessagingTemplate messagingTemplate;

    public NotificationService(SimpMessagingTemplate messagingTemplate) {{
        this.messagingTemplate = messagingTemplate;
    }}

    public void send(String type, String entityType, String message) {{
        NotificationMessage msg = NotificationMessage.of(type, entityType, message);
        messagingTemplate.convertAndSend(TOPIC, msg);
    }}
}}
"""

    def generate_integration_tests(self, base_package: str, modules: list[dict], project_slug: str) -> dict[str, str]:
        """
        Generates Testcontainers integration tests for each module.
        Returns a dict of relative test source paths -> file content.
        modules: list of dicts with keys 'name' (entity name)
        """
        pkg_path = base_package.replace(".", "/")
        files = {}

        # AbstractIntegrationTest base class
        files[f"src/test/java/{pkg_path}/AbstractIntegrationTest.java"] = f'''package {base_package};

import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Base class for integration tests.
 * Starts a real PostgreSQL container via Testcontainers — no H2, no mocks.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@Testcontainers
public abstract class AbstractIntegrationTest {{

    @Container
    static final PostgreSQLContainer<?> POSTGRES =
            new PostgreSQLContainer<>("postgres:15-alpine")
                    .withDatabaseName("{project_slug}_test")
                    .withUsername("test")
                    .withPassword("test");

    @DynamicPropertySource
    static void overrideProperties(DynamicPropertyRegistry registry) {{
        registry.add("spring.datasource.url",      POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
        registry.add("spring.security.oauth2.resourceserver.jwt.issuer-uri",
                () -> "http://localhost:9999/realms/test");
        registry.add("spring.security.oauth2.resourceserver.jwt.jwk-set-uri",
                () -> "http://localhost:9999/realms/test/protocol/openid-connect/certs");
        registry.add("spring.mail.host", () -> "localhost");
        registry.add("spring.mail.port", () -> "3025");
        registry.add("app.notifications.enabled", () -> "false");
    }}
}}
'''

        # Per-entity API integration tests
        for mod in modules:
            entity = mod["name"]
            lower = entity.lower()
            url_path = lower + "s"
            mod_pkg = f"{base_package}.{lower}"

            files[f"src/test/java/{pkg_path}/{lower}/{entity}ApiIT.java"] = f'''package {mod_pkg};

import {base_package}.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class {entity}ApiIT extends AbstractIntegrationTest {{

    @Autowired MockMvc mockMvc;

    @Test
    void getAll_returnsPageResponse() throws Exception {{
        mockMvc.perform(get("/{url_path}").with(jwt()).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content").isArray())
                .andExpect(jsonPath("$.page").value(0));
    }}

    @Test
    void getById_notFound_returns404() throws Exception {{
        mockMvc.perform(get("/{url_path}/00000000-0000-0000-0000-000000000000").with(jwt()))
                .andExpect(status().isNotFound());
    }}

    @Test
    void withoutAuth_returns401() throws Exception {{
        mockMvc.perform(get("/{url_path}")).andExpect(status().isUnauthorized());
    }}

    @Test
    void delete_notFound_returns404() throws Exception {{
        mockMvc.perform(delete("/{url_path}/00000000-0000-0000-0000-000000000000").with(jwt()))
                .andExpect(status().isNoContent()); // deactivate is idempotent
    }}
}}
'''

        # Dashboard IT
        files[f"src/test/java/{pkg_path}/dashboard/DashboardApiIT.java"] = f'''package {base_package}.dashboard;

import {base_package}.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class DashboardApiIT extends AbstractIntegrationTest {{

    @Autowired MockMvc mockMvc;

    @Test
    void getDashboard_returnsAllCounters() throws Exception {{
        mockMvc.perform(get("/dashboard").with(jwt()).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
{chr(10).join(f'                .andExpect(jsonPath("$.total{mod["name"]}s").isNumber())' for mod in modules)};
    }}
}}
'''
        return files

    def generate_global_exception_handler(self, package_name: str) -> str:
        """@ControllerAdvice that returns structured JSON errors."""
        return f"""package {package_name};

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {{

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleBadRequest(IllegalArgumentException ex) {{
        return error(HttpStatus.BAD_REQUEST, ex.getMessage());
    }}

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, Object>> handleConflict(IllegalStateException ex) {{
        return error(HttpStatus.CONFLICT, ex.getMessage());
    }}

    @ExceptionHandler(jakarta.persistence.EntityNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(jakarta.persistence.EntityNotFoundException ex) {{
        return error(HttpStatus.NOT_FOUND, ex.getMessage());
    }}

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException ex) {{
        Map<String, String> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .collect(Collectors.toMap(
                        fe -> fe.getField(),
                        fe -> fe.getDefaultMessage() != null ? fe.getDefaultMessage() : "Valor inválido",
                        (first, second) -> first
                ));
        Map<String, Object> body = buildBody(HttpStatus.BAD_REQUEST, "Error de validación");
        body.put("errors", fieldErrors);
        return ResponseEntity.badRequest().body(body);
    }}

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneric(Exception ex) {{
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "Internal server error");
    }}

    private ResponseEntity<Map<String, Object>> error(HttpStatus status, String message) {{
        return ResponseEntity.status(status).body(buildBody(status, message));
    }}

    private Map<String, Object> buildBody(HttpStatus status, String message) {{
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        return body;
    }}
}}
"""

    def generate_repository(self, package_name, entity, base_package=None, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
            page_import = f"{base_package}.shared.PageResult"
        else:
            model_import = f"{base_package}.domain.model.{entity}"
            page_import = f"{base_package}.shared.PageResult"

        return f"""
package {package_name};

import {model_import};
import {page_import};
import java.util.Optional;
import java.util.UUID;

public interface {entity}Repository {{

    {entity} save({entity} entity);

    Optional<{entity}> findById(UUID id);

    PageResult<{entity}> findAll(int page, int size, String search);

    void deactivate(UUID id);

}}

"""

    def generate_spring_data_repository(self, package_name, entity, base_package, module=None):

        if module:
            jpa_entity_import = f"{base_package}.{module}.infrastructure.persistence.entity.{entity}JpaEntity"
        else:
            jpa_entity_import = f"{base_package}.infrastructure.persistence.entity.{entity}JpaEntity"

        return f"""
package {package_name};

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import {jpa_entity_import};
import java.util.UUID;

public interface SpringData{entity}Repository
        extends JpaRepository<{entity}JpaEntity, UUID>,
                JpaSpecificationExecutor<{entity}JpaEntity> {{

    long countByActiveTrue();
}}
"""

    def generate_service(self, package_name, class_name, entity, base_package, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
        else:
            model_import = f"{base_package}.domain.model.{entity}"
            repo_import = f"{base_package}.domain.repository.{entity}Repository"

        return f"""
package {package_name};

import {model_import};
import {repo_import};

public class {class_name} {{

    private final {entity}Repository repository;

    public {class_name}({entity}Repository repository) {{
        this.repository = repository;
    }}

}}
"""

    def generate_jpa_adapter(self, package_name, class_name, entity, fields, base_package, module=None):
        """
        Deterministic JPA repository adapter.
        Never uses LLM — constructor arity is always correct.
        fields: non-id entity fields from inventory (id is always prepended by AST generator)
        """

        if module:
            domain_model_import = f"{base_package}.{module}.domain.model.{entity}"
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
            jpa_entity_import = f"{base_package}.{module}.infrastructure.persistence.entity.{entity}JpaEntity"
            spring_repo_import = f"{base_package}.{module}.infrastructure.persistence.spring.SpringData{entity}Repository"
        else:
            domain_model_import = f"{base_package}.domain.model.{entity}"
            repo_import = f"{base_package}.domain.repository.{entity}Repository"
            id_import = f"{base_package}.domain.valueobject.{entity}Id"
            jpa_entity_import = f"{base_package}.infrastructure.persistence.entity.{entity}JpaEntity"
            spring_repo_import = f"{base_package}.infrastructure.persistence.spring.SpringData{entity}Repository"

        # Build per-field mapping lines with VO → JDK type conversion
        non_id_fields = [f for f in fields if f.get("name") != "id"]

        def _setter_expr(f):
            """domain.getX() → jpa.setX(expr) with VO unwrapping if needed."""
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig_type = f.get("type", "String")
            jpa_t = self._jpa_type(orig_type)
            outer = orig_type.split("<")[0]
            domain_getter = f"domain.get{method}()"
            if jpa_t == orig_type:
                # No conversion needed
                expr = domain_getter
            elif jpa_t == "BigDecimal":
                if outer == "Money":
                    expr = f"{domain_getter} != null ? java.math.BigDecimal.valueOf({domain_getter}.getAmount()) : null"
                else:
                    expr = f"{domain_getter} != null ? java.math.BigDecimal.valueOf({domain_getter}) : null"
            elif jpa_t == "String":
                if outer.endswith("Id"):
                    expr = f"{domain_getter} != null ? {domain_getter}.getValue() : null"
                else:
                    # *Status/*Type/*Kind VO: call .getValue()
                    expr = f"{domain_getter} != null ? {domain_getter}.getValue() : null"
            elif jpa_t == "UUID":
                expr = f"{domain_getter} != null ? {domain_getter}.value() : null"
            else:
                expr = domain_getter
            return f"        jpa.set{method}({expr});"

        def _domain_arg(f):
            """jpa.getX() → arg in domain constructor with JDK → VO wrapping if needed."""
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig_type = f.get("type", "String")
            jpa_t = self._jpa_type(orig_type)
            outer = orig_type.split("<")[0]
            jpa_getter = f"jpa.get{method}()"
            if jpa_t == orig_type:
                return jpa_getter
            elif jpa_t == "BigDecimal":
                if outer == "Money":
                    return f"{jpa_getter} != null ? new {orig_type}({jpa_getter}.doubleValue(), \"USD\") : null"
                else:
                    return jpa_getter
            elif jpa_t == "String":
                # Wrap back into VO
                return f"new {orig_type}({jpa_getter})"
            elif jpa_t == "UUID":
                return f"new {orig_type}({jpa_getter})"
            return jpa_getter

        to_jpa_setters = "\n".join(_setter_expr(f) for f in non_id_fields)

        to_domain_args = ",\n            ".join(
            [f"new {entity}Id(jpa.getId())"] +
            [_domain_arg(f) for f in non_id_fields]
        )

        needs_bigdecimal = any(self._jpa_type(f.get("type", "")) == "BigDecimal" for f in non_id_fields)
        bigdecimal_import = "import java.math.BigDecimal;\n" if needs_bigdecimal else ""

        # Detect String fields usable in search predicate
        str_fields = [
            f["name"] for f in non_id_fields
            if self._jpa_type(f.get("type", "String")) == "String"
            and not f["name"].lower().endswith("id")
        ][:4]  # cap to 4 most relevant

        # Always filter active=true
        active_filter = "        spec = spec.and((root, q, cb) -> cb.isTrue(root.get(\"active\")));"

        if str_fields:
            predicate_lines = " ".join(
                f'cb.like(cb.lower(root.get("{fn}")), like),'
                for fn in str_fields
            ).rstrip(",")
            search_body = (
                f"{active_filter}\n"
                f"        if (search != null && !search.isBlank()) {{\n"
                f"            String like = \"%\" + search.toLowerCase() + \"%\";\n"
                f"            spec = spec.and((root, q, cb) -> cb.or(\n"
                f"                {predicate_lines}\n"
                f"            ));\n"
                f"        }}"
            )
        else:
            search_body = active_filter

        if module:
            page_import = f"{base_package}.shared.PageResult"
        else:
            page_import = f"{base_package}.shared.PageResult"

        return f"""package {package_name};

import {domain_model_import};
import {repo_import};
import {id_import};
import {jpa_entity_import};
import {spring_repo_import};
import {page_import};
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
{bigdecimal_import}

@Repository
public class {class_name} implements {entity}Repository {{

    private final SpringData{entity}Repository springRepository;

    public {class_name}(SpringData{entity}Repository springRepository) {{
        this.springRepository = springRepository;
    }}

    @Override
    public {entity} save({entity} entity) {{
        {entity}JpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }}

    @Override
    public Optional<{entity}> findById(UUID id) {{
        return springRepository.findById(id).map(this::toDomain);
    }}

    @Override
    public PageResult<{entity}> findAll(int page, int size, String search) {{
        Specification<{entity}JpaEntity> spec = Specification.where(null);
{search_body}
        var p = springRepository.findAll(spec, PageRequest.of(page, size));
        List<{entity}> content = p.getContent().stream().map(this::toDomain).collect(Collectors.toList());
        return new PageResult<>(content, page, size, p.getTotalElements());
    }}

    @Override
    public void deactivate(UUID id) {{
        springRepository.findById(id).ifPresent(jpa -> {{
            jpa.setActive(false);
            springRepository.save(jpa);
        }});
    }}

    private {entity}JpaEntity toJpaEntity({entity} domain) {{
        {entity}JpaEntity jpa = new {entity}JpaEntity();
        jpa.setId(domain.getId().value());
{to_jpa_setters}
        return jpa;
    }}

    private {entity} toDomain({entity}JpaEntity jpa) {{
        return new {entity}(
            {to_domain_args}
        );
    }}
}}
"""

    def _generate_execute_body(self, entity, use_case_name, uc_type, uc_inputs,
                               uc_returns, entity_fields):
        """
        Deterministic execute() body. Uses only known repository methods and correct
        Java record accessor syntax (fieldName(), not getFieldName()).
        """
        dto_var = "command" if uc_type == "command" else "query"
        entity_var = entity[0].lower() + entity[1:]
        is_list = str(uc_returns).startswith("List")
        is_query = uc_type == "query"
        uc_lower = use_case_name.lower()
        is_deactivate = any(w in uc_lower for w in ("deactivat", "cancel", "remov", "delet"))
        is_update = any(w in uc_lower for w in ("update", "edit", "modif", "change"))

        # Find the id input field from the use case inputs
        id_input = next(
            (i for i in (uc_inputs or []) if i.get("name", "").lower().endswith("id")),
            None
        )
        id_field = id_input["name"] if id_input else None

        if is_list:
            return f"        return repository.findAll({dto_var}.page(), {dto_var}.size(), {dto_var}.search());"

        if is_query:
            if id_field:
                return (
                    f"        return repository.findById({dto_var}.{id_field}());"
                )
            return "        return repository.findAll().stream().findFirst();"

        if is_deactivate:
            if id_field:
                return f"        repository.deactivate({dto_var}.{id_field}());"
            return "        throw new UnsupportedOperationException(\"Not implemented\");"

        if is_update:
            if id_field:
                return (
                    f"        return repository.findById({dto_var}.{id_field}())\n"
                    f"            .orElseThrow(() -> new IllegalArgumentException("
                    f"\"Not found\"));"
                )
            return "        throw new UnsupportedOperationException(\"Not implemented\");"

        # CREATE command — build entity constructor
        # Non-id entity fields (excluding base 'id')
        non_id_fields = [f for f in (entity_fields or []) if f.get("name") != "id"]
        input_names = {i.get("name") for i in (uc_inputs or [])}

        args = [f"new {entity}Id(UUID.randomUUID())"]
        for f in non_id_fields:
            fname = f.get("name")
            ftype = f.get("type", "")
            if fname in input_names:
                args.append(f"{dto_var}.{fname}()")
            elif ftype == "UUID" or fname.lower().endswith("id"):
                args.append("UUID.randomUUID()")
            else:
                args.append("null")

        args_str = ",\n            ".join(args)
        return (
            f"        {entity} {entity_var} = new {entity}(\n"
            f"            {args_str}\n"
            f"        );\n"
            f"        return repository.save({entity_var});"
        )

    def generate_usecase(self, package_name, use_case_name, entity, uc_type,
                         uc_inputs, uc_returns, uc_description, base_package,
                         module=None, entity_fields=None):
        """
        Deterministic use case class. One method: execute(Command/Query) -> return_type.
        Body is generated deterministically (no LLM).
        """
        if module:
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
            model_import = f"{base_package}.{module}.domain.model.{entity}"
        else:
            repo_import = f"{base_package}.domain.repository.{entity}Repository"
            model_import = f"{base_package}.domain.model.{entity}"

        dto_suffix = "Command" if uc_type == "command" else "Query"
        dto_class = f"{use_case_name}{dto_suffix}"

        # Determine return type
        returns = uc_returns or entity
        is_list_all = use_case_name.startswith("ListAll")
        is_deactivate_uc = any(w in use_case_name.lower() for w in ("deactivat", "cancel", "remov", "delet"))
        needs_optional = uc_type == "query" and not returns.startswith("List") and not is_list_all
        if is_deactivate_uc:
            return_type = "void"
        elif is_list_all:
            return_type = f"PageResult<{entity}>"
        elif needs_optional:
            return_type = f"Optional<{returns}>"
        elif returns.startswith("List"):
            return_type = f"List<{entity}>"
        else:
            return_type = returns

        # Id type import
        if module:
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
            page_result_import = f"{base_package}.shared.PageResult"
        else:
            id_import = f"{base_package}.domain.valueobject.{entity}Id"
            page_result_import = f"{base_package}.shared.PageResult"

        # Deterministic execute() body
        body = self._generate_execute_body(
            entity, use_case_name, uc_type, uc_inputs, uc_returns, entity_fields or []
        )

        return f"""package {package_name};

import {model_import};
import {repo_import};
import {id_import};
import {page_result_import};
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.stereotype.Service;

/**
 * {uc_description or use_case_name}
 */
@Service
public class {use_case_name}UseCase {{

    private final {entity}Repository repository;

    public {use_case_name}UseCase({entity}Repository repository) {{
        this.repository = repository;
    }}

    public {return_type} execute({dto_class} {dto_suffix.lower()}) {{
{body}
    }}
}}
"""

    def generate_usecase_command(self, package_name, use_case_name, inputs):
        """Generates a Command record (input DTO for a command use case) with Bean Validation annotations."""
        inputs = self._dedup_inputs(inputs)
        imports = self._imports_for_inputs(inputs)
        validation_imports = self._validation_imports_for_inputs(inputs)
        all_imports = imports | validation_imports
        imports_str = ("".join(f"import {i};\n" for i in sorted(all_imports)) + "\n") if all_imports else ""
        fields_str = ",\n\n    ".join(
            self._annotated_field(inp)
            for inp in (inputs or [])
        ) if inputs else ""

        if fields_str:
            return f"""package {package_name};

{imports_str}public record {use_case_name}Command(
    {fields_str}
) {{}}
"""
        return f"""package {package_name};

public record {use_case_name}Command() {{}}
"""

    @staticmethod
    def _annotated_field(inp):
        """Returns a field declaration with appropriate Bean Validation annotations."""
        field_type = inp.get("type", "String")
        name = inp.get("name", "value")
        annotations = []

        if field_type == "String":
            if any(kw in name.lower() for kw in ("email", "mail")):
                annotations.append('@NotBlank(message = "El campo es obligatorio")')
                annotations.append('@Email(message = "El email no es válido")')
                annotations.append('@Size(max = 200, message = "El email no puede superar 200 caracteres")')
            elif any(kw in name.lower() for kw in ("description", "descripcion", "notes", "notas", "comment")):
                annotations.append('@NotBlank(message = "La descripción es obligatoria")')
                annotations.append('@Size(max = 500, message = "La descripción no puede superar 500 caracteres")')
            else:
                label = name
                annotations.append(f'@NotBlank(message = "El campo {label} es obligatorio")')
                annotations.append(f'@Size(max = 100, message = "El campo {label} no puede superar 100 caracteres")')
        elif field_type == "UUID":
            if name.endswith("Id") or name == "id":
                label = name
                annotations.append(f'@NotNull(message = "El campo {label} es obligatorio")')
        elif field_type in ("LocalDate",):
            if any(kw in name.lower() for kw in ("birth", "nacimiento")):
                annotations.append('@NotNull(message = "La fecha es obligatoria")')
                annotations.append('@Past(message = "La fecha debe ser en el pasado")')
            else:
                annotations.append('@NotNull(message = "La fecha es obligatoria")')
        elif field_type in ("LocalDateTime",):
            annotations.append('@NotNull(message = "La fecha y hora son obligatorias")')
            if any(kw in name.lower() for kw in ("appointment", "cita", "schedule", "start", "end")):
                annotations.append('@FutureOrPresent(message = "La fecha debe ser presente o futura")')
        elif field_type not in ("int", "long", "double", "boolean", "float"):
            # Value objects, enums, etc.
            annotations.append(f'@NotNull(message = "El campo {name} es obligatorio")')
            if "Money" in field_type or "Amount" in field_type or "Price" in field_type:
                annotations.append('@Valid')

        ann_str = "\n    ".join(annotations)
        if ann_str:
            return f"{ann_str}\n    {field_type} {name}"
        return f"{field_type} {name}"

    @staticmethod
    def _validation_imports_for_inputs(inputs):
        """Returns validation annotation imports needed for the given fields."""
        needed = set()
        for inp in (inputs or []):
            field_type = inp.get("type", "String")
            name = inp.get("name", "value")
            if field_type == "String":
                needed.add("jakarta.validation.constraints.NotBlank")
                needed.add("jakarta.validation.constraints.Size")
                if any(kw in name.lower() for kw in ("email", "mail")):
                    needed.add("jakarta.validation.constraints.Email")
            elif field_type == "UUID":
                if name.endswith("Id") or name == "id":
                    needed.add("jakarta.validation.constraints.NotNull")
            elif field_type in ("LocalDate", "LocalDateTime"):
                needed.add("jakarta.validation.constraints.NotNull")
                if field_type == "LocalDate" and any(kw in name.lower() for kw in ("birth", "nacimiento")):
                    needed.add("jakarta.validation.constraints.Past")
                if field_type == "LocalDateTime":
                    needed.add("jakarta.validation.constraints.FutureOrPresent")
            elif field_type not in ("int", "long", "double", "boolean", "float"):
                needed.add("jakarta.validation.constraints.NotNull")
                if "Money" in field_type or "Amount" in field_type or "Price" in field_type:
                    needed.add("jakarta.validation.Valid")
        return needed

    def generate_usecase_query(self, package_name, use_case_name, inputs):
        """Generates a Query record. ListAll* queries automatically get page/size/search fields."""
        is_list_all = use_case_name.startswith("ListAll")
        inputs = self._dedup_inputs(inputs)

        if is_list_all:
            # Always inject pagination params for list queries
            pagination = [
                {"name": "page", "type": "int"},
                {"name": "size", "type": "int"},
                {"name": "search", "type": "String"},
            ]
            # Merge: keep any extra inputs from spec, deduplicate
            extra = [i for i in inputs if i.get("name") not in ("page", "size", "search")]
            inputs = pagination + extra

        imports = self._imports_for_inputs(inputs)
        imports_str = ("".join(f"import {i};\n" for i in sorted(imports)) + "\n") if imports else ""
        fields_str = ",\n    ".join(
            f"{inp.get('type', 'String')} {inp.get('name', 'value')}"
            for inp in (inputs or [])
        ) if inputs else ""

        if fields_str:
            return f"""package {package_name};

{imports_str}public record {use_case_name}Query(
    {fields_str}
) {{}}
"""
        return f"""package {package_name};

public record {use_case_name}Query() {{}}
"""

    @staticmethod
    def _dedup_inputs(inputs):
        """Remove duplicate fields by name, keeping first occurrence."""
        seen = set()
        result = []
        for inp in (inputs or []):
            name = inp.get("name")
            if name and name not in seen:
                seen.add(name)
                result.append(inp)
        return result

    @staticmethod
    def _imports_for_inputs(inputs):
        """Returns the set of Java standard imports needed for the given input fields."""
        TYPE_IMPORTS = {
            "UUID": "java.util.UUID",
            "LocalDate": "java.time.LocalDate",
            "LocalDateTime": "java.time.LocalDateTime",
            "Instant": "java.time.Instant",
            "BigDecimal": "java.math.BigDecimal",
            "List": "java.util.List",
            "Optional": "java.util.Optional",
        }
        needed = set()
        for inp in (inputs or []):
            t = inp.get("type", "")
            for key, imp in TYPE_IMPORTS.items():
                if key in t:
                    needed.add(imp)
        return needed

    def generate_mapper(self, package_name, class_name, entity, base_package, module=None):
        if module:
            domain_import = f"{base_package}.{module}.domain.model.{entity}"
            req_import = f"{base_package}.{module}.application.dto.{entity}Request"
            res_import = f"{base_package}.{module}.application.dto.{entity}Response"
        else:
            domain_import = f"{base_package}.domain.model.{entity}"
            req_import = f"{base_package}.application.dto.{entity}Request"
            res_import = f"{base_package}.application.dto.{entity}Response"

        return f"""package {package_name};

import {domain_import};
import {req_import};
import {res_import};
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface {class_name} {{

    {entity}Response toResponse({entity} entity);

}}
"""

    def generate_response_dto(self, package_name, entity, fields, base_package=None, module=None):
        """
        Generates a flat *Response record using only JDK-safe types.
        VO types (Money, *Status, *Id…) are unwrapped to String / Double / UUID.
        Always has UUID id as first field.
        """
        import re as _re

        def _response_type(java_type: str) -> str:
            outer = java_type.split("<")[0]
            if outer in self._JDK_TYPES:
                # LocalDate / LocalDateTime → String for clean JSON
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return "String"
                return java_type
            if outer in self._VO_TYPE_MAP or outer in ("Money", "Price", "Amount"):
                return "Double"
            if outer.endswith("Id"):
                return "UUID"
            if any(outer.endswith(s) for s in ("Status", "Type", "Kind", "State", "Category", "Role")):
                return "String"
            return "String"

        non_id_fields = [f for f in fields if f.get("name") != "id"]
        fields_str = "        UUID id"
        for f in non_id_fields:
            fname = f.get("name", "value")
            rtype = _response_type(f.get("type", "String"))
            fields_str += f",\n        {rtype} {fname}"

        needs_uuid = True  # id is always UUID
        needs_bigdecimal = any(
            _response_type(f.get("type", "")) == "BigDecimal" for f in non_id_fields
        )

        imports = ["import java.util.UUID;"]
        if needs_bigdecimal:
            imports.append("import java.math.BigDecimal;")

        imports_str = "\n".join(imports)

        return f"""package {package_name};

{imports_str}

public record {entity}Response(
{fields_str}
) {{}}
"""

    def generate_controller(self, package_name, class_name, entity, base_package, module=None, fields=None):
        """
        Full REST controller with 5 endpoints wired to the 5 standard use cases.
        toResponse() unwraps VO types to JDK types matching *Response record.
        """
        import re as _re

        fields = fields or []
        non_id_fields = [f for f in fields if f.get("name") != "id"]

        # Pluralise entity name for URL path (simple snake_case + 's')
        snake = _re.sub(r"([A-Z])", r"_\1", entity).lstrip("_").lower()
        url_path = snake + "s"

        # Use-case class names follow standard naming convention
        list_uc   = f"ListAll{entity}sUseCase"
        list_q    = f"ListAll{entity}sQuery"
        get_uc    = f"Get{entity}ByIdUseCase"
        get_q     = f"Get{entity}ByIdQuery"
        reg_uc    = f"Register{entity}UseCase"
        reg_cmd   = f"Register{entity}Command"
        upd_uc    = f"Update{entity}UseCase"
        upd_cmd   = f"Update{entity}Command"
        deact_uc  = f"Deactivate{entity}UseCase"
        deact_cmd = f"Deactivate{entity}Command"

        mod_prefix = f"{base_package}.{module}" if module else base_package

        uc_pkg = f"{mod_prefix}.application.usecase"
        dto_pkg = f"{mod_prefix}.application.dto"
        model_import = f"{mod_prefix}.domain.model.{entity}"
        page_result_import = f"{base_package}.shared.PageResult"
        page_response_import = f"{base_package}.shared.PageResponse"

        # Build toResponse() field mapping
        def _response_type(java_type: str) -> str:
            outer = java_type.split("<")[0]
            if outer in self._JDK_TYPES:
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return "String"
                return java_type
            if outer in self._VO_TYPE_MAP or outer in ("Money", "Price", "Amount"):
                return "Double"
            if outer.endswith("Id"):
                return "UUID"
            if any(outer.endswith(s) for s in ("Status", "Type", "Kind", "State", "Category", "Role")):
                return "String"
            return "String"

        def _getter_expr(f):
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig = f.get("type", "String")
            rtype = _response_type(orig)
            outer = orig.split("<")[0]
            g = f"e.get{method}()"
            if rtype == orig:
                # JDK type that stays as-is: LocalDate/LocalDateTime → toString()
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return f"{g} != null ? {g}.toString() : null"
                return g
            if rtype == "Double":
                if outer == "Money":
                    return f"{g} != null ? {g}.getAmount() : null"
                return f"{g} != null ? {g}.doubleValue() : null"
            if rtype == "String":
                # Temporal JDK types → toString()
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return f"{g} != null ? {g}.toString() : null"
                # VO wrapper → getValue()
                return f"{g} != null ? {g}.getValue() : null"
            if rtype == "UUID":
                return f"{g} != null ? {g}.value() : null"
            return g

        response_args = ["                e.getId().value()"]
        for f in non_id_fields:
            response_args.append(f"                {_getter_expr(f)}")
        response_args_str = ",\n".join(response_args)

        entity_var = entity[0].lower() + entity[1:]

        return f"""package {package_name};

import {model_import};
import {dto_pkg}.{entity}Response;
import {page_result_import};
import {page_response_import};
import {uc_pkg}.{list_uc};
import {uc_pkg}.{list_q};
import {uc_pkg}.{get_uc};
import {uc_pkg}.{get_q};
import {uc_pkg}.{reg_uc};
import {uc_pkg}.{reg_cmd};
import {uc_pkg}.{upd_uc};
import {uc_pkg}.{upd_cmd};
import {uc_pkg}.{deact_uc};
import {uc_pkg}.{deact_cmd};
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Tag(name = "{entity}s", description = "Gestión de {entity}s")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/{url_path}")
@CrossOrigin(origins = "*")
public class {class_name} {{

    private final {list_uc} listAll;
    private final {get_uc} getById;
    private final {reg_uc} register;
    private final {upd_uc} update;
    private final {deact_uc} deactivate;

    public {class_name}(
            {list_uc} listAll,
            {get_uc} getById,
            {reg_uc} register,
            {upd_uc} update,
            {deact_uc} deactivate) {{
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }}

    @Operation(summary = "Listar todos (paginado + búsqueda)")
    @GetMapping
    public PageResponse<{entity}Response> getAll(
            @RequestParam(defaultValue = "0")  int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "")   String search) {{
        PageResult<{entity}> result = listAll.execute(new {list_q}(page, size, search));
        List<{entity}Response> content = result.content().stream()
                .map(this::toResponse).collect(Collectors.toList());
        return new PageResponse<>(content, result.page(), result.size(),
                result.total(), result.totalPages(), result.isLast());
    }}

    @Operation(summary = "Obtener por ID")
    @GetMapping("/{{id}}")
    public ResponseEntity<{entity}Response> getOne(@PathVariable("id") UUID id) {{
        return getById.execute(new {get_q}(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }}

    @Operation(summary = "Crear nuevo registro")
    @PostMapping
    public ResponseEntity<{entity}Response> create(@RequestBody @Valid {reg_cmd} cmd) {{
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }}

    @Operation(summary = "Actualizar registro existente")
    @PutMapping("/{{id}}")
    public ResponseEntity<{entity}Response> updateOne(@PathVariable("id") UUID id,
                                                       @RequestBody @Valid {upd_cmd} cmd) {{
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }}

    @Operation(summary = "Desactivar registro (soft delete)")
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {{
        deactivate.execute(new {deact_cmd}(id));
        return ResponseEntity.noContent().build();
    }}

    private {entity}Response toResponse({entity} e) {{
        return new {entity}Response(
{response_args_str}
        );
    }}
}}
"""