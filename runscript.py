import os, sys
import click
import questionary
from pathlib import Path
from subprocess import run

sys.path.insert(0, os.path.abspath("."))

controllers = Path(os.path.abspath(__file__)).parents[0] / "src" / "controllers"


class ChoiceOption(click.Option):
    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception("ChoiceOption type arg must be click.Choice")

        if self.prompt:
            prompt_text = "{}:\n{}\n".format(
                self.prompt,
                "\n".join(
                    f"{idx: >4}: {c}"
                    for idx, c in enumerate(self.type.choices, start=1)
                ),
            )
            self.prompt = prompt_text

    def process_prompt_value(self, ctx, value, prompt_type):
        if value is not None:
            index = prompt_type(value, self, ctx)
            return self.type.choices[index - 1]

    def prompt_for_value(self, ctx):
        default = self.get_default(ctx)
        prompt_type = click.IntRange(min=1, max=len(self.type.choices))
        return click.prompt(
            self.prompt,
            default=default,
            type=prompt_type,
            hide_input=self.hide_input,
            show_choices=False,
            confirmation_prompt=self.confirmation_prompt,
            value_proc=lambda x: self.process_prompt_value(ctx, x, prompt_type),
        )


@click.command()
@click.option(
    "--hash-type",
    prompt="Select an Option: \n",
    type=click.Choice(
        [
            "Build sampling matrices from ocean measurements",
            "Extract Darwin surface data and build dataframes",
            "Create samples from Darwin Model output",
            "Build training sets for GAMs",
            "Train GAMs models and make predictions",
            "Analyse results from GAMs predictions",
            "Generate figures",
            "Exit",
        ],
        case_sensitive=False,
    ),
    cls=ChoiceOption,
)
def cli(hash_type):
    if hash_type == "Build sampling matrices from ocean measurements":
        print("\n")
        run(["python", f"{controllers}/OceanMeasurementsController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Extract Darwin surface data and build dataframes":
        print("\n")
        run(["python", f"{controllers}/ModelDataController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Create samples from Darwin Model output":
        print("\n")
        run(["python", f"{controllers}/ModelSamplingController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Build training sets for GAMs":
        print("\n")
        run(["python", f"{controllers}/TrainingSetController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Train GAMs models and make predictions":
        print("\n")
        run(["python", f"{controllers}/GamsController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Analyse results from GAMs predictions":
        print("\n")
        run(["python", f"{controllers}/AnalysisController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Generate figures":
        print("\n")
        run(["python", f"{controllers}/FinalFigsController.py"])
        print("-- done --")
        cli()

    elif hash_type == "Exit":
        print("\n", "Exiting program... byeeee", "\n")


if __name__ == "__main__":
    print("\n")
    cli()
