from dataclasses import dataclass, field
from drafter import *

@dataclass
class Substance:
    name: str = ""
    actual_mass: float = 0.0
    molar_mass: float = 0.0
    is_product: bool = False
    is_reactant: bool = False
    coefficient: int = 1

@dataclass
class State:
    substances: list[Substance] = field(default_factory=list)
    show_heat_analysis: bool = False
    heat_input: str = ""
    limiting_reagent: str = "TBD"
    theoretical_yield: str = "TBD"
    remaining_masses: list[str] = field(default_factory=list)
    heat_analysis: str = "TBD"
    percent_yield: str = "TBD"
    
    want_limiting: bool = True
    want_theoretical: bool = True
    want_remaining: bool = True
    want_percent: bool = True
    want_heat_page: bool = False


#Page 1
@route
def index(state: State) -> Page:
    return reaction_entry_page(state)

@route
def reaction_entry_page(state: State) -> Page:
    return Page(state, [
        Header("Step 1: Enter Chemical Reaction"),
        Text("Please enter a balanced chemical reaction (e.g., 2H2 + O2 -> 2H2O):"),
        TextBox("reaction_input", "2H2 + O2 -> 2H2O"),
        Button("Parse & Next", parse_reaction)
    ])

@route
def parse_reaction(state: State, reaction_input: str) -> Page:
    state.substances = []
    if "->" in reaction_input:
        reactants_part, products_part = reaction_input.split("->")
        for r in reactants_part.split("+"):
            r_name = r.strip()
            if r_name:
                state.substances.append(Substance(name=r_name, is_reactant=True))
        for p in products_part.split("+"):
            p_name = p.strip()
            if p_name:
                state.substances.append(Substance(name=p_name, is_product=True))
    else:
        state.substances = [
            Substance(name="Reactant A", is_reactant=True),
            Substance(name="Product B", is_product=True)
        ]
        
    return data_entry_page(state)


#Page 2
@route
def data_entry_page(state: State) -> Page:
    content = [
        Header("Step 2: Enter Substance Masses"),
        Text("Enter the mass (in grams) for each substance based on your reaction:")
    ]
    
    for i, sub in enumerate(state.substances):
        role_text = "Reactant" if sub.is_reactant else "Product"
        content.append(Text(f"Mass for {sub.name} ({role_text}):"))
        content.append(TextBox(f"mass_{i}", "0.0"))

    content.append(Button("Save Masses & Next", mass_save))
    content.append(Button("Back to Reaction", reaction_entry_page))
    
    return Page(state, content)

@route
def mass_save(state: State, **kwargs) -> Page:
    for i, sub in enumerate(state.substances):
        key = f"mass_{i}"
        if key in kwargs:
            try:
                sub.actual_mass = float(kwargs[key])
            except ValueError:
                sub.actual_mass = 0.0
                
    return options_page(state)


# Page 3
@route
def options_page(state: State) -> Page:
    return Page(state, [
        Header("Step 3: Select Desired Calculations"),
        Text("Check the specific data you want to get about this reaction:"),
        
        Text("Calculate Limiting Reagent:"),
        CheckBox("want_limiting"),
        
        Text("Calculate Theoretical Yield:"),
        CheckBox("want_theoretical"),
        
        Text("Calculate Remaining Masses of Reactants:"),
        CheckBox("want_remaining"),
        
        Text("Calculate Percent Yield:"),
        CheckBox("want_percent"),
        
        HorizontalRule(),
        Text("Do you want to include a Heat Analysis? (Checking this will open Page 4)"),
        CheckBox("want_heat_page"),
        
        Button("Confirm Options", options_chose),
        Button("Back to Masses", data_entry_page)
    ])

@route
def options_chose(state: State, want_limiting: bool, want_theoretical: bool, 
                  want_remaining: bool, want_percent: bool, want_heat_page: bool) -> Page:
    state.want_limiting = want_limiting
    state.want_theoretical = want_theoretical
    state.want_remaining = want_remaining
    state.want_percent = want_percent
    state.want_heat_page = want_heat_page
    
    if state.want_heat_page:
        return heat_analysis_entry_page(state)
    else:
        return data_calculate(state)


# Page 4(optional)
@route
def heat_analysis_entry_page(state: State) -> Page:
    return Page(state, [
        Header("Step 4: Heat Analysis Data"),
        Text("Please enter the Heat of Reaction (ΔH in kJ/mol):"),
        TextBox("heat_input", "0.0"),
        Button("Calculate Results", heat_reaction_save),
        Button("Back to Options", options_page)
    ])

@route
def heat_reaction_save(state: State, heat_input: str) -> Page:
    state.show_heat_analysis = True
    state.heat_input = heat_input
    return data_calculate(state)


# Page 5
@route
def data_calculate(state: State) -> Page:
    state.limiting_reagent = "[Placeholder: Calculated Limiting Reagent]" if state.want_limiting else "Skipped"
    state.theoretical_yield = "[Placeholder: Calculated Theoretical Yield]" if state.want_theoretical else "Skipped"
    state.percent_yield = "[Placeholder: Calculated Percent Yield]" if state.want_percent else "Skipped"
    state.remaining_masses = ["[Placeholder: Remaining Reactant Mass Example]"] if state.want_remaining else ["Skipped"]
    
    if state.show_heat_analysis:
        state.heat_analysis = f"[Placeholder: Heat Analysis Result, ΔH = {state.heat_input} kJ/mol]"
    else:
        state.heat_analysis = "Not Requested"
        
    return result_page(state)

@route
def result_page(state: State) -> Page:
    content = [
        Header("Step 5: Calculation Results"),
        Text(f"Limiting Reagent: {state.limiting_reagent}"),
        Text(f"Theoretical Yield: {state.theoretical_yield}"),
        Text(f"Percent Yield: {state.percent_yield}"),
        Text("Remaining Masses:")
    ]
    
    for item in state.remaining_masses:
        content.append(Text(f" - {item}"))
        
    if state.show_heat_analysis:
        content.append(HorizontalRule())
        content.append(Header("Heat Analysis Result"))
        content.append(Text(state.heat_analysis))
        
    content.append(HorizontalRule())
    content.append(Button("Start New Calculation", reaction_entry_page))
    
    return Page(state, content)


start_server(State())
