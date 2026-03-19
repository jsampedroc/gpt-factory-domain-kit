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

    def generate_file_storage_service(self, base_package: str) -> str:
        """
        Generates FileStorageService — stores uploaded files on the local filesystem
        under uploads/<entityType>/<entityId>/ and returns the stored filename.
        """
        return f"""package {base_package}.shared;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * Stores uploaded files on the local filesystem.
 * Files are saved under: <upload-dir>/<entityType>/<entityId>/<uuid>_<originalName>
 * In production replace with S3 / GCS / Azure Blob Storage.
 */
@Service
public class FileStorageService {{

    private final Path uploadRoot;

    public FileStorageService(@Value("${{app.upload.dir:uploads}}") String uploadDir) {{
        this.uploadRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {{
            Files.createDirectories(this.uploadRoot);
        }} catch (IOException e) {{
            throw new UncheckedIOException("Cannot create upload directory", e);
        }}
    }}

    /**
     * Stores a file and returns its stored filename (UUID prefix + original name).
     */
    public String store(MultipartFile file, String entityType, String entityId) {{
        if (file.isEmpty()) {{
            throw new IllegalArgumentException("Cannot store empty file");
        }}
        String originalName = sanitize(file.getOriginalFilename());
        String storedName = UUID.randomUUID() + "_" + originalName;
        try {{
            Path dir = uploadRoot.resolve(entityType).resolve(entityId);
            Files.createDirectories(dir);
            file.transferTo(dir.resolve(storedName));
        }} catch (IOException e) {{
            throw new UncheckedIOException("Failed to store file " + originalName, e);
        }}
        return storedName;
    }}

    /**
     * Returns the absolute path for a stored file.
     */
    public Path load(String entityType, String entityId, String storedName) {{
        return uploadRoot.resolve(entityType).resolve(entityId).resolve(storedName).normalize();
    }}

    /**
     * Deletes a stored file. Returns true if the file existed and was deleted.
     */
    public boolean delete(String entityType, String entityId, String storedName) {{
        try {{
            return Files.deleteIfExists(load(entityType, entityId, storedName));
        }} catch (IOException e) {{
            return false;
        }}
    }}

    private String sanitize(String name) {{
        if (name == null || name.isBlank()) return "file";
        return name.replaceAll("[^a-zA-Z0-9._\\\\-]", "_");
    }}
}}
"""

    def generate_document_entity_sql(self) -> str:
        """
        Generates a Flyway migration SQL for the shared documents table.
        This table links uploaded files to any domain entity (polymorphic association).
        """
        return (
            "-- Documents: stores metadata for uploaded files linked to any domain entity\n"
            "CREATE TABLE IF NOT EXISTS documents (\n"
            "    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    entity_type   VARCHAR(64)  NOT NULL,\n"
            "    entity_id     UUID         NOT NULL,\n"
            "    original_name VARCHAR(255) NOT NULL,\n"
            "    stored_name   VARCHAR(255) NOT NULL,\n"
            "    content_type  VARCHAR(128),\n"
            "    file_size     BIGINT,\n"
            "    uploaded_by   VARCHAR(128),\n"
            "    uploaded_at   TIMESTAMP    NOT NULL DEFAULT now()\n"
            ");\n"
            "CREATE INDEX IF NOT EXISTS idx_documents_entity ON documents(entity_type, entity_id);\n"
        )

    def generate_document_controller(self, base_package: str) -> str:
        """
        Generates DocumentController — REST endpoints to upload/list/delete files
        for any domain entity. Mounted at /api/documents/{entityType}/{entityId}.
        """
        return f"""package {base_package}.shared;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.Instant;
import java.util.*;

/**
 * Handles file uploads and downloads for any domain entity.
 * Files are stored on disk by FileStorageService.
 * Metadata is kept in memory (replace with DB persistence for production).
 */
@RestController
@RequestMapping("/api/documents")
public class DocumentController {{

    private final FileStorageService storageService;
    // In-memory store: entityType+entityId -> list of metadata
    // Replace with a JPA repository backed by the documents table in production.
    private final Map<String, List<DocumentMeta>> store = new java.util.concurrent.ConcurrentHashMap<>();

    public DocumentController(FileStorageService storageService) {{
        this.storageService = storageService;
    }}

    @PostMapping(value = "/{{entityType}}/{{entityId}}",
                 consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentMeta> upload(
            @PathVariable String entityType,
            @PathVariable String entityId,
            @RequestParam("file") MultipartFile file,
            @AuthenticationPrincipal Jwt jwt) {{

        String uploader = jwt != null ? jwt.getSubject() : "anonymous";
        String storedName = storageService.store(file, entityType, entityId);
        DocumentMeta meta = new DocumentMeta(
                UUID.randomUUID().toString(), entityType, entityId,
                file.getOriginalFilename(), storedName,
                file.getContentType(), file.getSize(),
                uploader, Instant.now());
        store.computeIfAbsent(entityType + ":" + entityId, k -> new ArrayList<>()).add(meta);
        return ResponseEntity.ok(meta);
    }}

    @GetMapping("/{{entityType}}/{{entityId}}")
    public ResponseEntity<List<DocumentMeta>> list(
            @PathVariable String entityType,
            @PathVariable String entityId) {{
        return ResponseEntity.ok(store.getOrDefault(entityType + ":" + entityId, List.of()));
    }}

    @DeleteMapping("/{{entityType}}/{{entityId}}/{{storedName}}")
    public ResponseEntity<Void> delete(
            @PathVariable String entityType,
            @PathVariable String entityId,
            @PathVariable String storedName) {{
        storageService.delete(entityType, entityId, storedName);
        List<DocumentMeta> docs = store.get(entityType + ":" + entityId);
        if (docs != null) docs.removeIf(d -> d.storedName().equals(storedName));
        return ResponseEntity.noContent().build();
    }}

    public record DocumentMeta(
            String id,
            String entityType,
            String entityId,
            String originalName,
            String storedName,
            String contentType,
            long fileSize,
            String uploadedBy,
            Instant uploadedAt) {{}}
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

    def generate_appointment_reminder_scheduler(self, base_package: str) -> str:
        return f"""package {base_package}.shared;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Sends appointment reminder emails 24 hours before the scheduled time.
 * Runs every hour via @Scheduled(cron).
 * In production, track sent reminders in DB to avoid duplicates.
 */
@Service
@EnableScheduling
public class AppointmentReminderScheduler {{

    private static final Logger log = LoggerFactory.getLogger(AppointmentReminderScheduler.class);
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");

    private final JavaMailSender mailSender;

    public AppointmentReminderScheduler(JavaMailSender mailSender) {{
        this.mailSender = mailSender;
    }}

    /**
     * Runs every hour. Override in subclass or via bean to inject real appointment data.
     * This is the base implementation — wire with your AppointmentRepository.
     */
    @Scheduled(cron = "0 0 * * * *")
    public void sendReminders() {{
        log.info("[Scheduler] Checking appointments for 24h reminders at {{}}", LocalDateTime.now().format(FMT));
        // TODO: inject AppointmentRepository and query appointments in next 24h
        // List<Appointment> upcoming = appointmentRepo.findByDateBetween(now, now.plusHours(24));
        // upcoming.stream().filter(a -> !a.reminderSent()).forEach(this::sendReminder);
    }}

    protected void sendReminder(String patientEmail, String patientName,
                                 String dentistName, LocalDateTime appointmentDate) {{
        try {{
            SimpleMailMessage msg = new SimpleMailMessage();
            msg.setTo(patientEmail);
            msg.setSubject("Recordatorio de cita dental");
            msg.setText(String.format(
                "Hola %s,\\n\\nLe recordamos que tiene una cita con el/la Dr/a. %s " +
                "el día %s.\\n\\nSi necesita cancelar o modificar la cita, contacte con nosotros " +
                "con antelación.\\n\\nUn saludo,\\nClínica Dental",
                patientName, dentistName, appointmentDate.format(FMT)
            ));
            mailSender.send(msg);
            log.info("[Scheduler] Reminder sent to {{}}", patientEmail);
        }} catch (Exception e) {{
            log.error("[Scheduler] Failed to send reminder to {{}}: {{}}", patientEmail, e.getMessage());
        }}
    }}
}}
"""

    def generate_audit_log_entity(self, base_package: str) -> dict:
        pkg_path = base_package.replace('.', '/')
        return {
            f"src/main/java/{pkg_path}/shared/AuditLog.java": f"""package {base_package}.shared;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * Persists every CREATE/UPDATE/DELETE action for auditing purposes.
 * Records who did what, when, and on which entity.
 */
@Entity
@Table(name = "audit_log", indexes = {{
    @Index(name = "idx_audit_entity", columnList = "entity_type, entity_id"),
    @Index(name = "idx_audit_user", columnList = "performed_by"),
}})
public class AuditLog {{

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "entity_type", nullable = false, length = 64)
    private String entityType;

    @Column(name = "entity_id", length = 64)
    private String entityId;

    @Column(name = "action", nullable = false, length = 16)
    private String action; // CREATE | UPDATE | DELETE

    @Column(name = "performed_by", length = 128)
    private String performedBy;

    @Column(name = "performed_at", nullable = false)
    private Instant performedAt = Instant.now();

    @Column(name = "details", length = 2000)
    private String details;

    protected AuditLog() {{}}

    public AuditLog(String entityType, String entityId, String action,
                    String performedBy, String details) {{
        this.entityType = entityType;
        this.entityId = entityId;
        this.action = action;
        this.performedBy = performedBy;
        this.performedAt = Instant.now();
        this.details = details;
    }}

    public UUID getId() {{ return id; }}
    public String getEntityType() {{ return entityType; }}
    public String getEntityId() {{ return entityId; }}
    public String getAction() {{ return action; }}
    public String getPerformedBy() {{ return performedBy; }}
    public Instant getPerformedAt() {{ return performedAt; }}
    public String getDetails() {{ return details; }}
}}
""",
            f"src/main/java/{pkg_path}/shared/AuditLogRepository.java": f"""package {base_package}.shared;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, UUID> {{
    Page<AuditLog> findByEntityTypeAndEntityId(String entityType, String entityId, Pageable pageable);
    Page<AuditLog> findByPerformedBy(String performedBy, Pageable pageable);
}}
""",
            f"src/main/java/{pkg_path}/shared/AuditService.java": f"""package {base_package}.shared;

import org.springframework.stereotype.Service;

/**
 * Records audit events for domain entities.
 * Call from use cases after successful state changes.
 */
@Service
public class AuditService {{

    private final AuditLogRepository repository;

    public AuditService(AuditLogRepository repository) {{
        this.repository = repository;
    }}

    public void record(String entityType, String entityId,
                       String action, String performedBy, String details) {{
        repository.save(new AuditLog(entityType, entityId, action, performedBy, details));
    }}

    public void recordCreate(String entityType, String entityId, String performedBy) {{
        record(entityType, entityId, "CREATE", performedBy, null);
    }}

    public void recordUpdate(String entityType, String entityId, String performedBy, String changes) {{
        record(entityType, entityId, "UPDATE", performedBy, changes);
    }}

    public void recordDelete(String entityType, String entityId, String performedBy) {{
        record(entityType, entityId, "DELETE", performedBy, null);
    }}
}}
""",
            f"src/main/java/{pkg_path}/shared/AuditLogController.java": f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST endpoint for querying the audit log.
 * Restricted to ADMIN role.
 */
@RestController
@RequestMapping("/api/audit")
@Tag(name = "Audit Log", description = "Query audit trail — Admin only")
@PreAuthorize("hasRole('ADMIN')")
public class AuditLogController {{

    private final AuditLogRepository repository;

    public AuditLogController(AuditLogRepository repository) {{
        this.repository = repository;
    }}

    @GetMapping("/entity/{{type}}/{{id}}")
    @Operation(summary = "Get audit history for a specific entity")
    public ResponseEntity<Page<AuditLog>> byEntity(
            @PathVariable String type,
            @PathVariable String id,
            Pageable pageable) {{
        return ResponseEntity.ok(repository.findByEntityTypeAndEntityId(type, id, pageable));
    }}

    @GetMapping("/user/{{username}}")
    @Operation(summary = "Get audit history for a specific user")
    public ResponseEntity<Page<AuditLog>> byUser(
            @PathVariable String username,
            Pageable pageable) {{
        return ResponseEntity.ok(repository.findByPerformedBy(username, pageable));
    }}
}}
"""
        }

    def generate_waiting_room_websocket_handler(self, base_package: str) -> str:
        return f"""package {base_package}.shared;

import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

/**
 * WebSocket message handler for the waiting room feature.
 * Frontend publishes to /app/waiting-room, server broadcasts to /topic/waiting-room.
 */
@Controller
public class WaitingRoomHandler {{

    /**
     * Relay waiting room events (ADD, UPDATE, REMOVE) to all subscribers.
     * In production, persist queue state to DB for recovery on restart.
     */
    @MessageMapping("/waiting-room")
    @SendTo("/topic/waiting-room")
    public Object relay(Object event) {{
        return event;  // relay as-is; enrich here if needed
    }}
}}
"""

    def generate_insurance_entity(self, base_package: str) -> dict:
        pkg_path = base_package.replace('.', '/')
        return {
            f"src/main/java/{pkg_path}/shared/Insurance.java": f"""package {base_package}.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.time.LocalDate;
import java.util.UUID;

/**
 * Stores insurance/convenio data for a patient.
 * One patient can have at most one active insurance record.
 */
@Entity
@Table(name = "insurance")
public class Insurance {{

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "patient_id", nullable = false)
    private UUID patientId;

    @NotBlank
    @Column(name = "insurance_company", nullable = false, length = 128)
    private String insuranceCompany;

    @Column(name = "policy_number", length = 64)
    private String policyNumber;

    @Column(name = "coverage_type", length = 32)
    private String coverageType; // FULL | PARTIAL | DENTAL_ONLY | NONE

    @Min(0) @Max(100)
    @Column(name = "coverage_percent")
    private Integer coveragePercent;

    @Future
    @Column(name = "valid_until")
    private LocalDate validUntil;

    @Column(name = "notes", length = 500)
    private String notes;

    protected Insurance() {{}}

    public Insurance(UUID patientId, String insuranceCompany, String policyNumber,
                     String coverageType, Integer coveragePercent,
                     LocalDate validUntil, String notes) {{
        this.patientId = patientId;
        this.insuranceCompany = insuranceCompany;
        this.policyNumber = policyNumber;
        this.coverageType = coverageType;
        this.coveragePercent = coveragePercent;
        this.validUntil = validUntil;
        this.notes = notes;
    }}

    public UUID getId() {{ return id; }}
    public UUID getPatientId() {{ return patientId; }}
    public String getInsuranceCompany() {{ return insuranceCompany; }}
    public String getPolicyNumber() {{ return policyNumber; }}
    public String getCoverageType() {{ return coverageType; }}
    public Integer getCoveragePercent() {{ return coveragePercent; }}
    public LocalDate getValidUntil() {{ return validUntil; }}
    public String getNotes() {{ return notes; }}
}}
""",
            f"src/main/java/{pkg_path}/shared/InsuranceRepository.java": f"""package {base_package}.shared;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface InsuranceRepository extends JpaRepository<Insurance, UUID> {{
    Optional<Insurance> findByPatientId(UUID patientId);
}}
""",
            f"src/main/java/{pkg_path}/shared/InsuranceController.java": f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.UUID;

@RestController
@RequestMapping("/api/insurance")
@Tag(name = "Insurance", description = "Patient insurance / convenio management")
public class InsuranceController {{

    private final InsuranceRepository repository;

    public InsuranceController(InsuranceRepository repository) {{
        this.repository = repository;
    }}

    @GetMapping("/patient/{{patientId}}")
    @Operation(summary = "Get insurance for a patient")
    public ResponseEntity<Insurance> getByPatient(@PathVariable UUID patientId) {{
        return repository.findByPatientId(patientId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }}

    @PostMapping("/patient/{{patientId}}")
    @Operation(summary = "Create or update insurance for a patient")
    public ResponseEntity<Insurance> upsert(
            @PathVariable UUID patientId,
            @RequestBody InsuranceRequest req) {{
        Insurance insurance = repository.findByPatientId(patientId)
                .orElse(new Insurance(patientId, req.insuranceCompany(), req.policyNumber(),
                        req.coverageType(), req.coveragePercent(), req.validUntil(), req.notes()));
        return ResponseEntity.ok(repository.save(insurance));
    }}

    public record InsuranceRequest(
            String insuranceCompany,
            String policyNumber,
            String coverageType,
            Integer coveragePercent,
            LocalDate validUntil,
            String notes) {{}}
}}
"""
        }

    def generate_audit_log_sql(self) -> str:
        return (
            "-- Audit log: records all CREATE/UPDATE/DELETE actions\n"
            "CREATE TABLE IF NOT EXISTS audit_log (\n"
            "    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    entity_type   VARCHAR(64)  NOT NULL,\n"
            "    entity_id     VARCHAR(64),\n"
            "    action        VARCHAR(16)  NOT NULL,\n"
            "    performed_by  VARCHAR(128),\n"
            "    performed_at  TIMESTAMP    NOT NULL DEFAULT now(),\n"
            "    details       VARCHAR(2000)\n"
            ");\n"
            "CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);\n"
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(performed_by);\n\n"
            "-- Insurance / convenio per patient\n"
            "CREATE TABLE IF NOT EXISTS insurance (\n"
            "    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    patient_id         UUID         NOT NULL,\n"
            "    insurance_company  VARCHAR(128) NOT NULL,\n"
            "    policy_number      VARCHAR(64),\n"
            "    coverage_type      VARCHAR(32),\n"
            "    coverage_percent   INTEGER CHECK (coverage_percent BETWEEN 0 AND 100),\n"
            "    valid_until        DATE,\n"
            "    notes              VARCHAR(500)\n"
            ");\n"
            "CREATE INDEX IF NOT EXISTS idx_insurance_patient ON insurance(patient_id);\n"
        )

    def generate_treatment_plan(self, base_package: str) -> dict[str, str]:
        """
        Generates TreatmentPlan and TreatmentPlanItem JPA entities, repositories,
        service and REST controller. Returns dict of relative src paths -> content.
        """
        pkg_path = base_package.replace('.', '/')
        files = {}

        files[f'src/main/java/{pkg_path}/shared/TreatmentPlan.java'] = f"""package {base_package}.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "treatment_plans")
public class TreatmentPlan {{

    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotNull @Column(name = "patient_id", nullable = false)
    private UUID patientId;

    @Column(name = "dentist_id")
    private UUID dentistId;

    /** DRAFT | PRESENTED | ACCEPTED | REJECTED | COMPLETED */
    @Column(name = "status", nullable = false, length = 20)
    private String status = "DRAFT";

    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "created_at")
    private LocalDate createdAt = LocalDate.now();

    @Column(name = "expires_at")
    private LocalDate expiresAt;

    @Column(name = "notes", length = 1000)
    private String notes;

    protected TreatmentPlan() {{}}

    public TreatmentPlan(UUID patientId, UUID dentistId, LocalDate expiresAt, String notes) {{
        this.patientId = patientId;
        this.dentistId = dentistId;
        this.expiresAt = expiresAt;
        this.notes = notes;
    }}

    public UUID getId() {{ return id; }}
    public UUID getPatientId() {{ return patientId; }}
    public UUID getDentistId() {{ return dentistId; }}
    public String getStatus() {{ return status; }}
    public void setStatus(String status) {{ this.status = status; }}
    public BigDecimal getTotalAmount() {{ return totalAmount; }}
    public void setTotalAmount(BigDecimal totalAmount) {{ this.totalAmount = totalAmount; }}
    public LocalDate getCreatedAt() {{ return createdAt; }}
    public LocalDate getExpiresAt() {{ return expiresAt; }}
    public String getNotes() {{ return notes; }}
}}
"""

        files[f'src/main/java/{pkg_path}/shared/TreatmentPlanItem.java'] = f"""package {base_package}.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "treatment_plan_items")
public class TreatmentPlanItem {{

    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotNull @Column(name = "plan_id", nullable = false)
    private UUID planId;

    @Column(name = "tooth_number")
    private Integer toothNumber;

    @NotBlank @Column(name = "procedure_code", length = 32)
    private String procedureCode;

    @NotBlank @Column(name = "description", length = 255)
    private String description;

    @Positive @Column(name = "quantity")
    private Integer quantity = 1;

    @NotNull @Column(name = "unit_price", precision = 10, scale = 2)
    private BigDecimal unitPrice;

    @Column(name = "total_price", precision = 10, scale = 2)
    private BigDecimal totalPrice;

    @Column(name = "insurance_coverage", precision = 10, scale = 2)
    private BigDecimal insuranceCoverage = BigDecimal.ZERO;

    /** PENDING | ACCEPTED | COMPLETED | CANCELLED */
    @Column(name = "status", length = 16)
    private String status = "PENDING";

    protected TreatmentPlanItem() {{}}

    public TreatmentPlanItem(UUID planId, Integer toothNumber, String procedureCode,
                              String description, Integer quantity, BigDecimal unitPrice,
                              BigDecimal insuranceCoverage) {{
        this.planId = planId;
        this.toothNumber = toothNumber;
        this.procedureCode = procedureCode;
        this.description = description;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.totalPrice = unitPrice.multiply(BigDecimal.valueOf(quantity));
        this.insuranceCoverage = insuranceCoverage != null ? insuranceCoverage : BigDecimal.ZERO;
    }}

    public UUID getId() {{ return id; }}
    public UUID getPlanId() {{ return planId; }}
    public Integer getToothNumber() {{ return toothNumber; }}
    public String getProcedureCode() {{ return procedureCode; }}
    public String getDescription() {{ return description; }}
    public Integer getQuantity() {{ return quantity; }}
    public BigDecimal getUnitPrice() {{ return unitPrice; }}
    public BigDecimal getTotalPrice() {{ return totalPrice; }}
    public BigDecimal getInsuranceCoverage() {{ return insuranceCoverage; }}
    public String getStatus() {{ return status; }}
    public void setStatus(String status) {{ this.status = status; }}
}}
"""

        files[f'src/main/java/{pkg_path}/shared/TreatmentPlanRepository.java'] = f"""package {base_package}.shared;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface TreatmentPlanRepository extends JpaRepository<TreatmentPlan, UUID> {{
    List<TreatmentPlan> findByPatientIdOrderByCreatedAtDesc(UUID patientId);
    List<TreatmentPlan> findByStatus(String status);
}}
"""

        files[f'src/main/java/{pkg_path}/shared/TreatmentPlanItemRepository.java'] = f"""package {base_package}.shared;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface TreatmentPlanItemRepository extends JpaRepository<TreatmentPlanItem, UUID> {{
    List<TreatmentPlanItem> findByPlanIdOrderByToothNumber(UUID planId);
    void deleteByPlanId(UUID planId);
}}
"""

        files[f'src/main/java/{pkg_path}/shared/TreatmentPlanController.java'] = f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/treatment-plans")
@Tag(name = "Treatment Plans", description = "Patient treatment plan and budget management")
public class TreatmentPlanController {{

    private final TreatmentPlanRepository planRepo;
    private final TreatmentPlanItemRepository itemRepo;

    public TreatmentPlanController(TreatmentPlanRepository planRepo,
                                    TreatmentPlanItemRepository itemRepo) {{
        this.planRepo = planRepo;
        this.itemRepo = itemRepo;
    }}

    @GetMapping("/patient/{{patientId}}")
    @Operation(summary = "List all treatment plans for a patient")
    public ResponseEntity<List<TreatmentPlan>> listByPatient(@PathVariable UUID patientId) {{
        return ResponseEntity.ok(planRepo.findByPatientIdOrderByCreatedAtDesc(patientId));
    }}

    @GetMapping("/{{id}}/items")
    @Operation(summary = "Get items for a treatment plan")
    public ResponseEntity<List<TreatmentPlanItem>> getItems(@PathVariable UUID id) {{
        return ResponseEntity.ok(itemRepo.findByPlanIdOrderByToothNumber(id));
    }}

    @PostMapping
    @Operation(summary = "Create a new treatment plan with items")
    public ResponseEntity<TreatmentPlan> create(@RequestBody @Valid TreatmentPlanRequest req) {{
        TreatmentPlan plan = new TreatmentPlan(
                req.patientId(), req.dentistId(), req.expiresAt(), req.notes());
        plan = planRepo.save(plan);

        BigDecimal total = BigDecimal.ZERO;
        for (var item : req.items()) {{
            TreatmentPlanItem tpi = new TreatmentPlanItem(
                    plan.getId(), item.toothNumber(), item.procedureCode(),
                    item.description(), item.quantity(), item.unitPrice(),
                    item.insuranceCoverage());
            itemRepo.save(tpi);
            total = total.add(tpi.getTotalPrice());
        }}

        plan.setTotalAmount(total);
        return ResponseEntity.ok(planRepo.save(plan));
    }}

    @PatchMapping("/{{id}}/status")
    @Operation(summary = "Update treatment plan status")
    public ResponseEntity<TreatmentPlan> updateStatus(
            @PathVariable UUID id,
            @RequestBody StatusRequest req) {{
        return planRepo.findById(id).map(plan -> {{
            plan.setStatus(req.status());
            return ResponseEntity.ok(planRepo.save(plan));
        }}).orElse(ResponseEntity.notFound().build());
    }}

    @DeleteMapping("/{{id}}")
    @Operation(summary = "Delete a draft treatment plan")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {{
        itemRepo.deleteByPlanId(id);
        planRepo.deleteById(id);
        return ResponseEntity.noContent().build();
    }}

    public record TreatmentPlanRequest(
            UUID patientId,
            UUID dentistId,
            LocalDate expiresAt,
            String notes,
            List<ItemRequest> items) {{}}

    public record ItemRequest(
            Integer toothNumber,
            String procedureCode,
            String description,
            Integer quantity,
            BigDecimal unitPrice,
            BigDecimal insuranceCoverage) {{}}

    public record StatusRequest(String status) {{}}
}}
"""

        files[f'src/main/resources/db/migration/V6__treatment_plans.sql'] = """-- Treatment plans and itemized budget
CREATE TABLE IF NOT EXISTS treatment_plans (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID         NOT NULL,
    dentist_id    UUID,
    status        VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    total_amount  DECIMAL(10,2) DEFAULT 0,
    created_at    DATE         NOT NULL DEFAULT CURRENT_DATE,
    expires_at    DATE,
    notes         VARCHAR(1000)
);
CREATE INDEX IF NOT EXISTS idx_tp_patient ON treatment_plans(patient_id);
CREATE INDEX IF NOT EXISTS idx_tp_status ON treatment_plans(status);

CREATE TABLE IF NOT EXISTS treatment_plan_items (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id           UUID         NOT NULL REFERENCES treatment_plans(id) ON DELETE CASCADE,
    tooth_number      INTEGER,
    procedure_code    VARCHAR(32)  NOT NULL,
    description       VARCHAR(255) NOT NULL,
    quantity          INTEGER      NOT NULL DEFAULT 1,
    unit_price        DECIMAL(10,2) NOT NULL,
    total_price       DECIMAL(10,2) NOT NULL,
    insurance_coverage DECIMAL(10,2) DEFAULT 0,
    status            VARCHAR(16)  NOT NULL DEFAULT 'PENDING'
);
CREATE INDEX IF NOT EXISTS idx_tpi_plan ON treatment_plan_items(plan_id);
"""
        return files

    def generate_production_report_controller(self, base_package: str) -> str:
        """
        Generates ProductionReportController — REST endpoints for practice BI reports.
        Returns daily/monthly production aggregates, cancellation rates, top procedures.
        Uses native JPQL queries over existing JPA entities.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.*;

/**
 * Business intelligence and production reports for the dental practice.
 * All endpoints require ADMIN or DENTIST role.
 * In production, wire with real JPA repositories for each aggregate.
 */
@RestController
@RequestMapping("/api/reports")
@Tag(name = "Reports", description = "Practice production and BI reports")
@PreAuthorize("hasAnyRole('ADMIN', 'DENTIST')")
public class ProductionReportController {{

    /**
     * Monthly production summary.
     * Replace stub with: SELECT SUM(i.amount), COUNT(i) FROM Invoice i
     *   WHERE i.createdAt BETWEEN :from AND :to GROUP BY MONTH(i.createdAt)
     */
    @GetMapping("/production/monthly")
    @Operation(summary = "Monthly production totals for the last N months")
    public ResponseEntity<List<MonthlyProduction>> monthlyProduction(
            @RequestParam(defaultValue = "12") int months) {{
        List<MonthlyProduction> result = new ArrayList<>();
        YearMonth current = YearMonth.now();
        Random rnd = new Random(42); // deterministic stub data
        for (int i = months - 1; i >= 0; i--) {{
            YearMonth ym = current.minusMonths(i);
            result.add(new MonthlyProduction(
                    ym.toString(),
                    BigDecimal.valueOf(8000 + rnd.nextInt(6000)),
                    BigDecimal.valueOf(6000 + rnd.nextInt(4000)),
                    20 + rnd.nextInt(30)
            ));
        }}
        return ResponseEntity.ok(result);
    }}

    /**
     * Production breakdown by dentist for a date range.
     */
    @GetMapping("/production/by-dentist")
    @Operation(summary = "Production totals grouped by dentist")
    public ResponseEntity<List<DentistProduction>> byDentist(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {{
        // Stub — replace with: SELECT d.name, SUM(i.amount) FROM Invoice i JOIN Dentist d ON ...
        List<DentistProduction> result = List.of(
                new DentistProduction("Dr. García", BigDecimal.valueOf(12400), 45),
                new DentistProduction("Dra. Martínez", BigDecimal.valueOf(9800), 38),
                new DentistProduction("Dr. López", BigDecimal.valueOf(7200), 29)
        );
        return ResponseEntity.ok(result);
    }}

    /**
     * Top procedures by revenue and frequency.
     */
    @GetMapping("/production/top-procedures")
    @Operation(summary = "Top dental procedures by revenue")
    public ResponseEntity<List<ProcedureStats>> topProcedures(
            @RequestParam(defaultValue = "10") int limit) {{
        // Stub — replace with query over TreatmentPlanItem grouped by procedureCode
        List<ProcedureStats> result = List.of(
                new ProcedureStats("IMP001", "Implante dental", 42, BigDecimal.valueOf(63000)),
                new ProcedureStats("PRO002", "Corona zirconio", 68, BigDecimal.valueOf(40800)),
                new ProcedureStats("END002", "Endodoncia multirradicular", 95, BigDecimal.valueOf(28500)),
                new ProcedureStats("PRO001", "Corona metal-porcelana", 54, BigDecimal.valueOf(21600)),
                new ProcedureStats("OBT002", "Obturación 2 caras", 187, BigDecimal.valueOf(16830)),
                new ProcedureStats("PER002", "Raspado y alisado", 76, BigDecimal.valueOf(15200)),
                new ProcedureStats("BLA001", "Blanqueamiento", 63, BigDecimal.valueOf(12600)),
                new ProcedureStats("EXT002", "Extracción quirúrgica", 89, BigDecimal.valueOf(11125)),
                new ProcedureStats("OBT003", "Obturación 3 caras", 134, BigDecimal.valueOf(10720)),
                new ProcedureStats("PER001", "Tartrectomía", 210, BigDecimal.valueOf(10500))
        ).subList(0, Math.min(limit, 10));
        return ResponseEntity.ok(result);
    }}

    /**
     * Appointment cancellation / no-show analysis.
     */
    @GetMapping("/cancellations")
    @Operation(summary = "Cancellation and no-show rates by month")
    public ResponseEntity<List<CancellationStats>> cancellations(
            @RequestParam(defaultValue = "6") int months) {{
        List<CancellationStats> result = new ArrayList<>();
        YearMonth current = YearMonth.now();
        Random rnd = new Random(7);
        for (int i = months - 1; i >= 0; i--) {{
            YearMonth ym = current.minusMonths(i);
            int total = 80 + rnd.nextInt(40);
            int cancelled = 5 + rnd.nextInt(12);
            int noShow = 2 + rnd.nextInt(6);
            result.add(new CancellationStats(ym.toString(), total, cancelled, noShow,
                    Math.round((cancelled + noShow) * 100.0f / total)));
        }}
        return ResponseEntity.ok(result);
    }}

    /**
     * Revenue forecast based on accepted treatment plans.
     */
    @GetMapping("/revenue-forecast")
    @Operation(summary = "Revenue pipeline from accepted treatment plans")
    public ResponseEntity<RevenueForecast> revenueForecast() {{
        // Stub — replace with: SELECT SUM(tp.totalAmount) FROM TreatmentPlan tp WHERE tp.status = 'ACCEPTED'
        return ResponseEntity.ok(new RevenueForecast(
                BigDecimal.valueOf(48500),   // pipeline (ACCEPTED plans)
                BigDecimal.valueOf(23000),   // expected this month
                BigDecimal.valueOf(15200),   // expected next month
                37                           // number of open plans
        ));
    }}

    // ─── Response records ─────────────────────────────────────────────────────

    public record MonthlyProduction(String month, BigDecimal production, BigDecimal collected, int appointments) {{}}
    public record DentistProduction(String dentistName, BigDecimal total, int appointments) {{}}
    public record ProcedureStats(String code, String name, int count, BigDecimal revenue) {{}}
    public record CancellationStats(String month, int total, int cancelled, int noShow, int ratePercent) {{}}
    public record RevenueForecast(BigDecimal pipeline, BigDecimal thisMonth, BigDecimal nextMonth, int openPlans) {{}}
}}
"""

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

    def generate_consent_controller(self, base_package: str) -> str:
        """
        Generates ConsentController.java — CRUD + sign endpoints for informed consent forms.
        Uses in-memory ConcurrentHashMap storage (replace with JPA in production).
        Round 27.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * REST controller for managing informed consent forms (consentimientos informados).
 * Round 27 — in-memory implementation. Wire with real repositories in production.
 */
@RestController
@RequestMapping("/api/consents")
@Tag(name = "Consents", description = "Gestion de consentimientos informados")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class ConsentController {{

    private static final Map<UUID, ConsentRecord> STORE = new ConcurrentHashMap<>();

    private static final String DEFAULT_CONSENT_TEXT =
        "CONSENTIMIENTO INFORMADO PARA TRATAMIENTO DENTAL\\n\\n" +
        "Yo, el/la abajo firmante, autorizo al profesional odontologo a realizar los procedimientos " +
        "de implantologia, endodoncia, extracciones y demas tratamientos dentales que se consideren " +
        "necesarios para el mantenimiento de mi salud bucodental, habiendo sido informado/a de los " +
        "riesgos y beneficios asociados a dichos procedimientos.\\n\\n" +
        "Declaro haber recibido explicacion sobre las alternativas de tratamiento disponibles, " +
        "los posibles riesgos e inconvenientes, las consecuencias previsibles de su realizacion " +
        "y las contraindicaciones. Me ha sido facilitada la oportunidad de formular preguntas " +
        "sobre el procedimiento y estas han sido contestadas de forma satisfactoria.\\n\\n" +
        "Entiendo que puedo revocar este consentimiento en cualquier momento antes del inicio " +
        "del procedimiento, sin que ello afecte a la atencion medica que deba recibir posteriormente. " +
        "Este documento se rige por la Ley 41/2002 de Autonomia del Paciente.";

    // ---------------------------------------------------------------
    // Endpoints
    // ---------------------------------------------------------------

    /** GET /api/consents/patient/{{patientId}} — list consents for a patient */
    @GetMapping("/patient/{{patientId}}")
    public ResponseEntity<List<ConsentResponse>> listByPatient(@PathVariable UUID patientId) {{
        List<ConsentResponse> result = STORE.values().stream()
                .filter(c -> c.patientId().equals(patientId))
                .map(ConsentController::toResponse)
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }}

    /** POST /api/consents — create a new consent record */
    @PostMapping
    public ResponseEntity<ConsentResponse> create(@RequestBody ConsentRequest req) {{
        String text = (req.consentText() != null && !req.consentText().isBlank())
                ? req.consentText()
                : DEFAULT_CONSENT_TEXT;
        ConsentRecord record = new ConsentRecord(
                UUID.randomUUID(),
                req.patientId(),
                "Paciente " + req.patientId().toString().substring(0, 8),
                req.dentistId(),
                "Dr. " + req.dentistId().toString().substring(0, 8),
                req.procedure(),
                text,
                req.date() != null ? req.date() : LocalDate.now(),
                "PENDIENTE",
                null
        );
        STORE.put(record.id(), record);
        return ResponseEntity.ok(toResponse(record));
    }}

    /** GET /api/consents/{{id}} — get a single consent by id */
    @GetMapping("/{{id}}")
    public ResponseEntity<ConsentResponse> getById(@PathVariable UUID id) {{
        ConsentRecord record = STORE.get(id);
        if (record == null) {{
            return ResponseEntity.notFound().build();
        }}
        return ResponseEntity.ok(toResponse(record));
    }}

    /** POST /api/consents/{{id}}/sign — patient signs the consent */
    @PostMapping("/{{id}}/sign")
    public ResponseEntity<ConsentResponse> sign(@PathVariable UUID id) {{
        ConsentRecord existing = STORE.get(id);
        if (existing == null) {{
            return ResponseEntity.notFound().build();
        }}
        String signedAt = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        ConsentRecord signed = new ConsentRecord(
                existing.id(),
                existing.patientId(),
                existing.patientName(),
                existing.dentistId(),
                existing.dentistName(),
                existing.procedure(),
                existing.consentText(),
                existing.date(),
                "FIRMADO",
                signedAt
        );
        STORE.put(id, signed);
        return ResponseEntity.ok(toResponse(signed));
    }}

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record ConsentRequest(
            UUID patientId,
            UUID dentistId,
            String procedure,
            String consentText,
            LocalDate date
    ) {{}}

    public record ConsentResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            String procedure,
            String consentText,
            LocalDate date,
            String status,
            String signedAt
    ) {{}}

    private record ConsentRecord(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            String procedure,
            String consentText,
            LocalDate date,
            String status,
            String signedAt
    ) {{}}

    private static ConsentResponse toResponse(ConsentRecord r) {{
        return new ConsentResponse(
                r.id(), r.patientId(), r.patientName(),
                r.dentistId(), r.dentistName(),
                r.procedure(), r.consentText(),
                r.date(), r.status(), r.signedAt()
        );
    }}
}}
"""

    def generate_patient_portal_controller(self, base_package: str) -> str:
        """
        Generates PatientPortalController — public REST endpoints for patient self-service.
        No @PreAuthorize — intentionally public. Uses stub data; wire real repos in production.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * Public-facing patient portal endpoints.
 * No authentication required — patients access using their patient ID.
 * In production, wire with real repositories and validate patient identity.
 */
@RestController
@RequestMapping("/api/portal")
@Tag(name = "Patient Portal", description = "Public endpoints for patient self-service")
public class PatientPortalController {{

    /**
     * Returns the appointment history for a given patient.
     * GET /api/portal/appointments?patientId={{uuid}}
     * Stub implementation — replace with real repository query.
     */
    @GetMapping("/appointments")
    @Operation(summary = "Obtener historial de citas del paciente")
    public ResponseEntity<List<AppointmentSummary>> getAppointments(
            @RequestParam UUID patientId) {{

        // Stub data — replace with: appointmentRepo.findByPatientId(patientId)
        List<AppointmentSummary> result = List.of(
                new AppointmentSummary(
                        UUID.randomUUID(),
                        "2025-11-10",
                        "Dr. García",
                        "Limpieza dental",
                        "COMPLETED"
                ),
                new AppointmentSummary(
                        UUID.randomUUID(),
                        "2025-12-15",
                        "Dra. Martínez",
                        "Revisión ortodoncia",
                        "CONFIRMED"
                )
        );
        return ResponseEntity.ok(result);
    }}

    /**
     * Accepts a new appointment request from a patient.
     * POST /api/portal/appointments/request
     */
    @PostMapping("/appointments/request")
    @Operation(summary = "Solicitar nueva cita (paciente)")
    public ResponseEntity<String> requestAppointment(
            @RequestBody AppointmentRequest request) {{

        // Stub — in production persist to a PendingAppointmentRequest entity
        // and trigger notification to clinic staff
        return ResponseEntity.ok(
                "Solicitud recibida para el paciente " + request.patientId() +
                " el " + request.date() + ". Le contactaremos para confirmar."
        );
    }}

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record AppointmentSummary(
            UUID id,
            String date,
            String dentist,
            String procedure,
            String status
    ) {{}}

    public record AppointmentRequest(
            UUID patientId,
            String date,
            String procedure,
            String notes
    ) {{}}
}}
"""

    def generate_stock_controller(self, base_package: str) -> str:
        """
        Generates StockController — inventory and supply management for clinic.
        ADMIN only. In-memory ConcurrentHashMap with 15 pre-populated dental supplies.
        Endpoints: list, add, update, movement (IN/OUT), low-stock alerts, movement history.
        Round 28.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Clinic supply and inventory management.
 * Pre-populated with 15 realistic dental supplies.
 * In production, replace in-memory store with a JPA repository.
 */
@RestController
@RequestMapping("/api/stock")
@Tag(name = "Stock", description = "Clinic supply and inventory management")
@PreAuthorize("hasAnyRole('ADMIN')")
public class StockController {{

    // ---------------------------------------------------------------
    // In-memory store
    // ---------------------------------------------------------------

    private final ConcurrentHashMap<UUID, StockItem> store = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<UUID, List<StockMovement>> movements = new ConcurrentHashMap<>();

    public StockController() {{
        seed();
    }}

    private void seed() {{
        addItem("Anestesia Articaína 4%",            "Anestésicos",              "cartucho",      20,  120, new BigDecimal("1.85"),   "DentalDep S.L.");
        addItem("Guantes de nitrilo (S)",             "EPIs",                     "caja 100u",      5,   22, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Guantes de nitrilo (M)",             "EPIs",                     "caja 100u",      5,   18, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Guantes de nitrilo (L)",             "EPIs",                     "caja 100u",      5,    4, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Mascarillas FFP2",                   "EPIs",                     "caja 20u",      10,   35, new BigDecimal("12.00"),  "Medistock S.A.");
        addItem("Gasas estériles",                    "Material quirúrgico",      "paquete 100u",   8,   50, new BigDecimal("4.20"),   "SurgePro");
        addItem("Implante Nobel Biocare Ø3.5",        "Implantes",                "unidad",         5,   12, new BigDecimal("185.00"), "Nobel Biocare");
        addItem("Composite Filtek Z350",              "Resinas",                  "jeringa 4g",     6,   20, new BigDecimal("28.50"),  "3M ESPE");
        addItem("Cemento ionómero de vidrio",         "Cementos",                 "polvo 25g",      4,   10, new BigDecimal("34.00"),  "GC Europe");
        addItem("Fresas de diamante redondas",        "Instrumental rotatorio",   "caja 10u",       3,    8, new BigDecimal("19.90"),  "Komet Dental");
        addItem("Papel de articular 200µm",           "Diagnóstico",              "caja 144 tiras", 2,    6, new BigDecimal("5.80"),   "Bausch");
        addItem("Hilo de retracción #2",              "Prótesis",                 "carrete",        3,    5, new BigDecimal("11.40"),  "Ultrapak");
        addItem("Ácido grabador 37%",                 "Adhesivos",                "jeringa 3ml",    5,   14, new BigDecimal("6.20"),   "Ivoclar");
        addItem("Adhesivo Optibond FL",               "Adhesivos",                "kit",            3,    0, new BigDecimal("62.00"),  "Kerr Dental");
        addItem("Sutura reabsorbible 3/0",            "Material quirúrgico",      "caja 12u",       4,    9, new BigDecimal("22.50"),  "Ethicon");
    }}

    private void addItem(String name, String category, String unit,
                         int minStock, int currentStock, BigDecimal unitPrice, String supplier) {{
        UUID id = UUID.randomUUID();
        String status = computeStatus(currentStock, minStock);
        store.put(id, new StockItem(id, name, category, unit, minStock, currentStock, unitPrice, supplier, status));
        movements.put(id, new ArrayList<>());
    }}

    private String computeStatus(int current, int min) {{
        if (current == 0)     return "CRITICAL";
        if (current <= min)   return "LOW";
        return "OK";
    }}

    // ---------------------------------------------------------------
    // Endpoints
    // ---------------------------------------------------------------

    @GetMapping
    @Operation(summary = "Listar todos los artículos (con filtro opcional ?search=)")
    public ResponseEntity<List<StockItem>> list(@RequestParam(required = false) String search) {{
        List<StockItem> items = new ArrayList<>(store.values());
        if (search != null && !search.isBlank()) {{
            String q = search.toLowerCase();
            items = items.stream()
                    .filter(i -> i.name().toLowerCase().contains(q)
                              || i.category().toLowerCase().contains(q)
                              || i.supplier().toLowerCase().contains(q))
                    .collect(Collectors.toList());
        }}
        items.sort(Comparator.comparing(StockItem::name));
        return ResponseEntity.ok(items);
    }}

    @PostMapping
    @Operation(summary = "Añadir nuevo artículo al stock")
    public ResponseEntity<StockItem> create(@RequestBody StockItemRequest req) {{
        UUID id = UUID.randomUUID();
        String status = computeStatus(req.currentStock(), req.minStock());
        StockItem item = new StockItem(id, req.name(), req.category(), req.unit(),
                req.minStock(), req.currentStock(), req.unitPrice(), req.supplier(), status);
        store.put(id, item);
        movements.put(id, new ArrayList<>());
        return ResponseEntity.ok(item);
    }}

    @PutMapping("/{{id}}")
    @Operation(summary = "Actualizar datos de un artículo")
    public ResponseEntity<StockItem> update(@PathVariable UUID id,
                                            @RequestBody StockItemRequest req) {{
        StockItem existing = store.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        String status = computeStatus(req.currentStock(), req.minStock());
        StockItem updated = new StockItem(id, req.name(), req.category(), req.unit(),
                req.minStock(), req.currentStock(), req.unitPrice(), req.supplier(), status);
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }}

    @PostMapping("/{{id}}/movement")
    @Operation(summary = "Registrar movimiento de stock (ENTRADA / SALIDA)")
    public ResponseEntity<StockItem> recordMovement(@PathVariable UUID id,
                                                    @RequestBody MovementRequest req) {{
        StockItem item = store.get(id);
        if (item == null) return ResponseEntity.notFound().build();

        int newStock = "IN".equalsIgnoreCase(req.type())
                ? item.currentStock() + req.quantity()
                : Math.max(0, item.currentStock() - req.quantity());

        StockMovement mov = new StockMovement(
                UUID.randomUUID(), id, req.type().toUpperCase(), req.quantity(), req.reason(),
                LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        movements.computeIfAbsent(id, k -> new ArrayList<>()).add(mov);

        String status = computeStatus(newStock, item.minStock());
        StockItem updated = new StockItem(id, item.name(), item.category(), item.unit(),
                item.minStock(), newStock, item.unitPrice(), item.supplier(), status);
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }}

    @GetMapping("/low")
    @Operation(summary = "Artículos con stock bajo o crítico (alertas)")
    public ResponseEntity<List<StockItem>> lowStock() {{
        List<StockItem> alerts = store.values().stream()
                .filter(i -> !"OK".equals(i.status()))
                .sorted(Comparator.comparing(StockItem::name))
                .collect(Collectors.toList());
        return ResponseEntity.ok(alerts);
    }}

    @GetMapping("/{{id}}/movements")
    @Operation(summary = "Historial de movimientos de un artículo")
    public ResponseEntity<List<StockMovement>> getMovements(@PathVariable UUID id) {{
        List<StockMovement> list = movements.getOrDefault(id, Collections.emptyList());
        List<StockMovement> sorted = new ArrayList<>(list);
        sorted.sort(Comparator.comparing(StockMovement::createdAt).reversed());
        return ResponseEntity.ok(sorted);
    }}

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record StockItem(
            UUID id,
            String name,
            String category,
            String unit,
            int minStock,
            int currentStock,
            BigDecimal unitPrice,
            String supplier,
            String status          // OK | LOW | CRITICAL
    ) {{}}

    public record StockItemRequest(
            String name,
            String category,
            String unit,
            int minStock,
            int currentStock,
            BigDecimal unitPrice,
            String supplier
    ) {{}}

    public record StockMovement(
            UUID id,
            UUID itemId,
            String type,           // IN | OUT
            int quantity,
            String reason,
            String createdAt
    ) {{}}

    public record MovementRequest(
            String type,           // IN | OUT
            int quantity,
            String reason
    ) {{}}
}}
"""

    def generate_prescription_controller(self, base_package: str) -> str:
        """
        Generates PrescriptionController — REST endpoints for electronic prescriptions.
        Requires ADMIN or DENTIST role. Uses in-memory ConcurrentHashMap stub storage.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Electronic prescriptions management.
 * Requires ADMIN or DENTIST role.
 * Uses in-memory stub storage — wire real repositories in production.
 */
@RestController
@RequestMapping("/api/prescriptions")
@Tag(name = "Prescriptions", description = "Electronic prescriptions management")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class PrescriptionController {{

    private final Map<UUID, PrescriptionResponse> store = new ConcurrentHashMap<>();

    // ---------------------------------------------------------------
    // GET /api/prescriptions/patient/{{patientId}}
    // ---------------------------------------------------------------

    @GetMapping("/patient/{{patientId}}")
    @Operation(summary = "Listar recetas de un paciente")
    public ResponseEntity<List<PrescriptionResponse>> getByPatient(
            @PathVariable UUID patientId) {{

        List<PrescriptionResponse> result = store.values().stream()
                .filter(p -> patientId.equals(p.patientId()))
                .collect(Collectors.toList());

        // Seed stub data when store is empty for demo purposes
        if (result.isEmpty()) {{
            PrescriptionResponse stub = new PrescriptionResponse(
                    UUID.randomUUID(),
                    patientId,
                    "Paciente Demo",
                    UUID.randomUUID(),
                    "Dr. García",
                    LocalDate.now().minusDays(3),
                    "Infección periodontal leve",
                    List.of(
                            new PrescriptionLine(
                                    "Amoxicilina 500mg",
                                    "500mg",
                                    "Cada 8 horas",
                                    7,
                                    "Tomar con alimentos"
                            ),
                            new PrescriptionLine(
                                    "Ibuprofeno 400mg",
                                    "400mg",
                                    "Cada 6 horas si hay dolor",
                                    5,
                                    "No superar 1200mg/día"
                            )
                    ),
                    "Revisión en 7 días",
                    "ACTIVA",
                    LocalDateTime.now().minusDays(3).format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            );
            store.put(stub.id(), stub);
            result = List.of(stub);
        }}

        return ResponseEntity.ok(result);
    }}

    // ---------------------------------------------------------------
    // POST /api/prescriptions
    // ---------------------------------------------------------------

    @PostMapping
    @Operation(summary = "Crear nueva receta electrónica")
    public ResponseEntity<PrescriptionResponse> create(
            @Valid @RequestBody PrescriptionRequest request) {{

        UUID id = UUID.randomUUID();
        PrescriptionResponse response = new PrescriptionResponse(
                id,
                request.patientId(),
                "Paciente " + request.patientId().toString().substring(0, 8),
                request.dentistId(),
                "Dr. Usuario",
                request.date() != null ? request.date() : LocalDate.now(),
                request.diagnosis(),
                request.lines() != null ? request.lines() : List.of(),
                request.notes(),
                "ACTIVA",
                LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        );
        store.put(id, response);
        return ResponseEntity.ok(response);
    }}

    // ---------------------------------------------------------------
    // GET /api/prescriptions/{{id}}
    // ---------------------------------------------------------------

    @GetMapping("/{{id}}")
    @Operation(summary = "Obtener receta por ID")
    public ResponseEntity<PrescriptionResponse> getById(@PathVariable UUID id) {{
        PrescriptionResponse p = store.get(id);
        if (p == null) {{
            return ResponseEntity.notFound().build();
        }}
        return ResponseEntity.ok(p);
    }}

    // ---------------------------------------------------------------
    // DELETE /api/prescriptions/{{id}}  — void / cancel
    // ---------------------------------------------------------------

    @DeleteMapping("/{{id}}")
    @Operation(summary = "Anular receta electrónica")
    public ResponseEntity<PrescriptionResponse> voidPrescription(@PathVariable UUID id) {{
        PrescriptionResponse existing = store.get(id);
        if (existing == null) {{
            return ResponseEntity.notFound().build();
        }}
        PrescriptionResponse voided = new PrescriptionResponse(
                existing.id(),
                existing.patientId(),
                existing.patientName(),
                existing.dentistId(),
                existing.dentistName(),
                existing.date(),
                existing.diagnosis(),
                existing.lines(),
                existing.notes(),
                "ANULADA",
                existing.createdAt()
        );
        store.put(id, voided);
        return ResponseEntity.ok(voided);
    }}

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record PrescriptionRequest(
            UUID patientId,
            UUID dentistId,
            LocalDate date,
            String diagnosis,
            List<PrescriptionLine> lines,
            String notes
    ) {{}}

    public record PrescriptionLine(
            String medication,
            String dosage,
            String frequency,
            int durationDays,
            String instructions
    ) {{}}

    public record PrescriptionResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            LocalDate date,
            String diagnosis,
            List<PrescriptionLine> lines,
            String notes,
            String status,
            String createdAt
    ) {{}}
}}
"""

    def generate_payment_controller(self, base_package: str) -> str:
        """
        Generates PaymentController — payment history and TPV endpoints.
        Round 29: Historial de Pagos y TPV.
        """
        return f"""package {base_package}.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Payment history and point-of-sale (TPV) controller.
 * Round 29 — in-memory stub; wire with real persistence in production.
 */
@RestController
@RequestMapping("/api/payments")
@Tag(name = "Payments", description = "Payment history and point of sale")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class PaymentController {{

    private static final Map<UUID, PaymentResponse> STORE = new ConcurrentHashMap<>();

    static {{
        String[][] demo = {{
            {{"a1b2c3d4-0001-0001-0001-000000000001","Ana López","f1000001-0000-0000-0000-000000000001","120.00","CASH","","PAID","2026-03-01T09:15:00","Limpieza dental"}},
            {{"a1b2c3d4-0002-0002-0002-000000000002","Carlos Ruiz","f1000002-0000-0000-0000-000000000002","350.00","CARD","TXN-4821","PAID","2026-03-03T10:30:00","Empaste molar"}},
            {{"a1b2c3d4-0003-0003-0003-000000000003","María García","f1000003-0000-0000-0000-000000000003","80.00","INSURANCE","SEG-001","PAID","2026-03-05T11:00:00","Revisión periódica"}},
            {{"a1b2c3d4-0004-0004-0004-000000000004","Pedro Sánchez","f1000004-0000-0000-0000-000000000004","900.00","TRANSFER","TRAN-9910","PAID","2026-03-07T12:45:00","Corona porcelana"}},
            {{"a1b2c3d4-0005-0005-0005-000000000005","Laura Martínez","f1000005-0000-0000-0000-000000000005","200.00","CARD","TXN-5533","PAID","2026-03-10T09:00:00","Blanqueamiento"}},
            {{"a1b2c3d4-0006-0006-0006-000000000006","Javier Torres","f1000006-0000-0000-0000-000000000006","45.00","CASH","","PAID","2026-03-12T14:20:00","Urgencia dolor"}},
            {{"a1b2c3d4-0007-0007-0007-000000000007","Sofía Díaz","f1000007-0000-0000-0000-000000000007","1200.00","INSURANCE","SEG-082","PAID","2026-03-14T16:00:00","Ortodoncia mensualidad"}},
            {{"a1b2c3d4-0008-0008-0008-000000000008","Miguel Fernández","f1000008-0000-0000-0000-000000000008","75.00","CASH","","PAID","2026-03-17T08:30:00","Radiografía panorámica"}},
            {{"a1b2c3d4-0009-0009-0009-000000000009","Elena Romero","f1000009-0000-0000-0000-000000000009","500.00","CARD","TXN-7741","PAID","2026-03-19T10:10:00","Implante fase 1"}},
            {{"a1b2c3d4-0010-0010-0010-000000000010","Roberto Jiménez","f1000010-0000-0000-0000-000000000010","160.00","TRANSFER","TRAN-3301","PAID","2026-03-19T11:45:00","Endodoncia"}}
        }};
        for (String[] d : demo) {{
            UUID id = UUID.randomUUID();
            STORE.put(id, new PaymentResponse(
                id,
                UUID.fromString(d[0]), d[1],
                UUID.fromString(d[2]),
                new BigDecimal(d[3]), d[4], d[5], d[6], d[7], d[8]
            ));
        }}
    }}

    /** GET /api/payments/patient/{{patientId}} */
    @GetMapping("/patient/{{patientId}}")
    @Operation(summary = "Historial de pagos de un paciente")
    public ResponseEntity<List<PaymentResponse>> getByPatient(@PathVariable UUID patientId) {{
        List<PaymentResponse> result = STORE.values().stream()
                .filter(p -> p.patientId().equals(patientId))
                .sorted(Comparator.comparing(PaymentResponse::createdAt).reversed())
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }}

    /** POST /api/payments */
    @PostMapping
    @Operation(summary = "Registrar un pago")
    public ResponseEntity<PaymentResponse> createPayment(@RequestBody PaymentRequest req) {{
        UUID id = UUID.randomUUID();
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        PaymentResponse saved = new PaymentResponse(
                id, req.patientId(), "Paciente", req.invoiceId(),
                req.amount(), req.method(),
                req.reference() != null ? req.reference() : "",
                "PAID", now,
                req.notes() != null ? req.notes() : ""
        );
        STORE.put(id, saved);
        return ResponseEntity.ok(saved);
    }}

    /** GET /api/payments/summary/today */
    @GetMapping("/summary/today")
    @Operation(summary = "Resumen de caja del día")
    public ResponseEntity<DailySummary> getTodaySummary() {{
        LocalDate today = LocalDate.now();
        DateTimeFormatter fmt = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        List<PaymentResponse> todayPayments = STORE.values().stream()
                .filter(p -> {{
                    try {{ return LocalDateTime.parse(p.createdAt(), fmt).toLocalDate().equals(today); }}
                    catch (Exception e) {{ return false; }}
                }})
                .collect(Collectors.toList());
        BigDecimal total = BigDecimal.ZERO, cash = BigDecimal.ZERO,
                   card  = BigDecimal.ZERO, transfer = BigDecimal.ZERO, insurance = BigDecimal.ZERO;
        for (PaymentResponse p : todayPayments) {{
            total = total.add(p.amount());
            switch (p.method()) {{
                case "CASH"     -> cash     = cash.add(p.amount());
                case "CARD"     -> card     = card.add(p.amount());
                case "TRANSFER" -> transfer = transfer.add(p.amount());
                case "INSURANCE"-> insurance= insurance.add(p.amount());
            }}
        }}
        return ResponseEntity.ok(new DailySummary(today, total, cash, card, transfer, insurance, todayPayments.size()));
    }}

    /** GET /api/payments/summary/monthly?months=6 */
    @GetMapping("/summary/monthly")
    @Operation(summary = "Ingresos mensuales por método de pago")
    public ResponseEntity<List<MonthlyPaymentSummary>> getMonthlySummary(
            @RequestParam(defaultValue = "6") int months) {{
        DateTimeFormatter fmt = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        DateTimeFormatter monthFmt = DateTimeFormatter.ofPattern("yyyy-MM");
        LocalDate cutoff = LocalDate.now().minusMonths(months - 1L).withDayOfMonth(1);
        Map<String, MonthlyPaymentSummary> grouped = new LinkedHashMap<>();
        STORE.values().stream()
                .filter(p -> {{
                    try {{ return !LocalDateTime.parse(p.createdAt(), fmt).toLocalDate().isBefore(cutoff); }}
                    catch (Exception e) {{ return false; }}
                }})
                .forEach(p -> {{
                    String month;
                    try {{ month = LocalDateTime.parse(p.createdAt(), fmt).format(monthFmt); }}
                    catch (Exception e) {{ month = "unknown"; }}
                    grouped.compute(month, (k, ex) -> {{
                        if (ex == null) ex = new MonthlyPaymentSummary(k, BigDecimal.ZERO, BigDecimal.ZERO,
                                BigDecimal.ZERO, BigDecimal.ZERO, BigDecimal.ZERO);
                        return new MonthlyPaymentSummary(k,
                            ex.total().add(p.amount()),
                            ex.cash().add("CASH".equals(p.method())      ? p.amount() : BigDecimal.ZERO),
                            ex.card().add("CARD".equals(p.method())      ? p.amount() : BigDecimal.ZERO),
                            ex.transfer().add("TRANSFER".equals(p.method())  ? p.amount() : BigDecimal.ZERO),
                            ex.insurance().add("INSURANCE".equals(p.method()) ? p.amount() : BigDecimal.ZERO));
                    }});
                }});
        List<MonthlyPaymentSummary> result = new ArrayList<>(grouped.values());
        result.sort(Comparator.comparing(MonthlyPaymentSummary::month));
        return ResponseEntity.ok(result);
    }}

    public record PaymentRequest(
            UUID patientId,
            UUID invoiceId,
            BigDecimal amount,
            String method,
            String reference,
            String notes
    ) {{}}

    public record PaymentResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID invoiceId,
            BigDecimal amount,
            String method,
            String reference,
            String status,
            String createdAt,
            String notes
    ) {{}}

    public record DailySummary(
            LocalDate date,
            BigDecimal total,
            BigDecimal cash,
            BigDecimal card,
            BigDecimal transfer,
            BigDecimal insurance,
            int count
    ) {{}}

    public record MonthlyPaymentSummary(
            String month,
            BigDecimal total,
            BigDecimal cash,
            BigDecimal card,
            BigDecimal transfer,
            BigDecimal insurance
    ) {{}}
}}
"""