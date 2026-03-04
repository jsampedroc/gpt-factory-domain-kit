def auto_fix_java_code(code: str, issues: list):

    fixed = code

    for issue in issues:

        if issue == "Double space in class declaration":
            fixed = fixed.replace("class  ", "class ")

        if issue == "TODO left in generated code":
            fixed = fixed.replace("TODO", "")

    return fixed