import pandas as pd
import numpy as np
import textwrap
import csv
import random
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

lifepaths_path = "../data/Ataraxia_Lifepaths_v1.6.4.csv"
traits_path = "../data/traits.csv"

# Function to display DataFrame with adaptive formatting
def display_df_cli(df, columns, terminal_width=120):
    title_width = 20
    years_width = 15
    resources_width = 15
    traits_width = 15
    skills_start = title_width + years_width + resources_width + 4 * 3  # Adjust if adding more columns

    # Adjust header based on available columns
    header_parts = ['TITLE', 'TIME (YEARS)', 'RESOURCES (GP)']
    if 'Traits' in df.columns:
        header_parts.append('TRAITS')
        skills_start += traits_width + 3  # Adjust skills start if traits column exists
    header_parts.append('SKILLS')
    
    header = "|".join(f"{part:<{width}}" for part, width in zip(header_parts, [title_width, years_width, resources_width, traits_width, terminal_width - skills_start]))
    print(header)
    print('-' * terminal_width)

    for _, row in df.iterrows():
        row_parts = [f"{row['Title']:<{title_width}}", f"{row['Time (years)']:<{years_width}}", f"{row['Resources (gp)']:<{resources_width}}"]
        if 'Traits' in df.columns:
            row_parts.append(f"{row['Traits']:<{traits_width}}")
        wrapped_skills = textwrap.wrap(row['Skills'], width=terminal_width - skills_start)
        first_skill_line_text = wrapped_skills.pop(0) if wrapped_skills else ""
        row_parts.append(first_skill_line_text)
        
        print("|".join(row_parts))
        
        for skill_line in wrapped_skills:
            print(' ' * skills_start + skill_line)

# Function to display skills neatly
def display_skills(skill_dict, per_line=5):
    print("\nSkills:")
    skills_formatted = [f"{skill}: {count}" for skill, count in skill_dict.items()]
    for i in range(0, len(skills_formatted), per_line):
        print(", ".join(skills_formatted[i:i+per_line]))
        
def roll_stats_and_calculate_attributes():
    # Roll stats
    stats = {
        'Will': random.randint(1, 6),
        'Strength': random.randint(1, 6),
        'Agility': random.randint(1, 6),
        'Intellect': random.randint(1, 6),
        'Fortitude': random.randint(1, 6),
        'Endurance': random.randint(1, 6)
    }

    # Calculate attributes
    attributes = {
        'Morale': stats['Will'] + stats['Intellect'],
        'Vitality': stats['Strength'] + stats['Fortitude'],
        'Stamina': stats['Agility'] + stats['Endurance']
    }

    return stats, attributes

def print_final_character_summary(df, char_name):
    # Add 'Traits' column with random choices from loaded_trait_list to the DataFrame
    # df['Traits'] = [random.choice(loaded_trait_list) for _ in range(len(df))]
    
    # After finishing lifepath selection, compile final character data
    lifepaths = df['Title'].tolist()  # Extract the list of lifepaths
    age = df['Time (years)'].sum()  # Calculate total age
    resources = df['Resources (gp)'].sum()  # Calculate total resources
    
    # Skill calculation logic
    skill_ls = df['Skills'].str.split(',').explode().str.strip().tolist()
    skill_dict = {k: v for k, v in zip(*np.unique(skill_ls, return_counts=True))}
    
    # Printing final character summary
    print(f'\nFINAL CHARACTER: {char_name}')
    print(f'Lifepaths: {", ".join(lifepaths)}')
    print(f'Age: {age} years')
    print(f'Resources: {resources} gold\n')
    
    # Assuming roll_stats_and_calculate_attributes is defined elsewhere and returns stats and attributes
    stats, attributes = roll_stats_and_calculate_attributes()
    
    print("\nStats")
    stats_keys = list(stats.keys())
    for i in range(0, len(stats_keys), 3):  # Process three stats per line
        line = "    ".join(f"{stats_keys[j]}: {stats[stats_keys[j]]}".ljust(20) for j in range(i, min(i+3, len(stats_keys))))
        print(line)

    print("\nAttributes")
    for attribute, value in attributes.items():
        print(f"{attribute}: {value}".ljust(20), end="    ")
    print("\n")  # Ensure newline after attributes
    
    # Display DataFrame in CLI
    display_df_cli(df, ['Title', 'Time (years)', 'Resources (gp)', 'Traits'])
    
    print("Skills:")
    for skill, count in skill_dict.items():
        print(f"  {skill}: {count}")

def main():
    pd.set_option('display.max_colwidth', None)

    # Load data
    df = pd.read_csv(lifepaths_path)
    start_df = df.loc[df['Title'].str.contains("Born")]
    df['skill list'] = df['Skills'].apply(lambda x: [item.strip() for item in x.split(',')])
    df['lead list'] = df['Leads'].apply(lambda x: [item.strip() for item in x.split(',')])

    with open(traits_path, 'r', encoding='utf-8') as csvfile:
        loaded_trait_list = [row[0] for row in csv.reader(csvfile, delimiter=' ')]

    lp_df = pd.DataFrame(columns=df.columns)
    
    while True:
        # Improved Lifepaths Display
        if not lp_df.empty:
            print(f"\nCurrent Lifepaths: {', '.join(lp_df['Title'])}")
            print(f"Traits: {', '.join(lp_df['Traits'])}")
        else:
            print("Current Lifepaths: None")
        print(f"Age: {lp_df['Time (years)'].sum()} years")
        print(f"Resources: {lp_df['Resources (gp)'].sum()} gold\n")

        # Enhanced Skills Display
        if not lp_df.empty:
            skill_ls = lp_df['Skills'].str.split(',').explode().str.strip().tolist()
            skill_dict = {k: v for k, v in zip(*np.unique(skill_ls, return_counts=True))}
            print("Skills:")
            for skill, count in skill_dict.items():
                print(f"  {skill}: {count}")
        else:
            print("Skills: None")

        continue_flag = input("\nWould you like to add another Lifepath? (Y/N) ").strip().upper()
        if continue_flag == 'Y':
            if lp_df.empty:
                display_df_cli(start_df, ['Title', 'Time (years)', 'Resources (gp)', 'Traits', 'Skills'])
            else:
                leads = set(lp_df.iloc[-1]['lead list']) | {"Outcast"}
                choice_df = df[df['Title'].isin(leads)]
                display_df_cli(choice_df, ['Title', 'Time (years)', 'Resources (gp)', 'Traits', 'Skills'])
            
            title = input('\nWhat Lifepath do you choose? (or "random")').strip()
            if title.upper() == "RANDOM":
                selected_df = start_df if lp_df.empty else choice_df
                title = selected_df.sample(n=1)['Title'].iloc[0]
            selected_row = df[df['Title'].str.upper() == title.upper()].copy(deep=True)
            selected_row.loc[:, 'Traits'] = random.choice(loaded_trait_list) # Assign a random trait
            lp_df = lp_df.append(selected_row, ignore_index=True)
        else:
            break
    char_name = input("\nWhat is your character's name? ")

    # Call to print the final character summary
    print_final_character_summary(lp_df, char_name)

if __name__ == "__main__":
    main()
