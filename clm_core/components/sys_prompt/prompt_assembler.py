from clm_core.components.sys_prompt._prompt_template_validator import BoundPromptValidator
from clm_core.components.sys_prompt._schemas import PromptTemplate, ValidationLevel


class PromptAssembler:
    def __init__(self):
        self._bound_validator = BoundPromptValidator()

    def assemble_system_prompt(
        self,
        template: PromptTemplate,
        runtime_values: dict,
    ) -> str:
        """
        Bind runtime values into NL template
        Parameters
        ----------
        template
        runtime_values

        Returns
        -------

        """
        bound_nl = template.bind(**runtime_values)

        issues = self._bound_validator.validate(bound_nl)
        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        if errors:
            raise RuntimeError(
                f"Bound prompt validation failed: {[e.message for e in errors]}"
            )

        final_prompt = f"{template.compressed}\n\n{bound_nl}"

        return final_prompt
