rule all:
    input:
        "figure.pdf"

rule compute_power:
    input:
        "power_calculation_config.yaml"
    output:
        controls="power_controls.csv",
        balanced="power_balanced.csv",
        fixedN="power_fixedN.csv"
    shell:
        "python power_calculation.py {input} ."

rule build_pdf:
    input:
        tex="figure.tex",
        controls="power_controls.csv",
        balanced="power_balanced.csv",
        fixedN="power_fixedN.csv"
    output:
        "figure.pdf"
    shell:
        """
        pdflatex -interaction=nonstopmode figure.tex
        """