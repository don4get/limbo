import numpy as np
import scipy.stats as stats

from limbo.demography.config import average_age_young_worker, \
    average_fertility_min_age, average_fertility_max_age, average_age_retired_worker, shape_parameter, scale_parameter, \
    average_life_expectancy, current_year, current_population


def simulate_model(population, fecondity_rate=2.1, duration_years=30, plot=False, debug=False):
    populations = [population]
    number_of_workers = sum(population[average_age_young_worker:average_age_retired_worker])
    number_of_retired = sum(population[average_age_retired_worker:])
    ratio_worker_per_retired = number_of_retired / number_of_workers

    ratios = [ratio_worker_per_retired]
    immigrations = [0]
    pension_ages = [65]

    if debug:
        print(f"Population in year {current_year}: {sum(population)}")
    for index, year in enumerate(range(current_year, current_year + duration_years)):
        population = simulate_year(population, fecondity_rate, debug)

        populations.append(population)

        number_of_workers = sum(population[average_age_young_worker:average_age_retired_worker])

        number_of_retired = sum(population[average_age_retired_worker:])

        ratio_worker_per_retired = number_of_retired / number_of_workers
        if debug:
            print(f"Population in year {year}: {sum(population)}")
            print(f"Ratio worker per retired: {ratio_worker_per_retired}")

        ratios.append(ratio_worker_per_retired)

        immigrations.append(sum(populations[index]) - sum(populations[index + 1]))

        ratios2 = [sum(population[i:]) / sum(population[average_age_young_worker:i]) for i in range(40, 70)]
        legal_retirement_age = abs(np.array(ratios2) - ratios[0]).argmin() + 40
        pension_ages.append(legal_retirement_age)

    return populations, ratios, immigrations, pension_ages


def simulate_year(population, fecondity_rate, debug=False):
    born = simulate_births(population, fecondity_rate, debug)
    dead = simulate_deaths(population, debug)
    population = population - dead
    for i in range(len(population)):
        if population[i] < 1:
            population[i] = 0
    population = np.insert(population, 0, born[0])
    population = population[population > 1]
    return population


def simulate_births(population, fecondity_rate, debug=False):
    born = np.zeros(len(population))
    fertile_women = sum(population[average_fertility_min_age:average_fertility_max_age]) / 2
    fertile_duration = average_fertility_max_age - average_fertility_min_age
    born[0] = fertile_women * fecondity_rate / fertile_duration
    percentage_born = sum(born) / sum(population)
    if debug:
        print(f"Sum of born: {sum(born)}")
        print(f"Percentage of born: {percentage_born}")

    return born


def simulate_deaths(population, debug=False):
    dead = np.zeros(len(population))
    for age, number in enumerate(population):
        dead[age] = number * death_proba[age]

    percentage_dead = sum(dead) / sum(population)
    if debug:
        print(f"Sum of dead: {sum(dead)}")
        print(f"Percentage of dead: {percentage_dead}")

    return dead


def death_probability_by_age(age, shape, scale, life_expectancy):
    """
    Compute the death probability by age using the Weibull distribution.

    Parameters:
    - age: The age at which to compute the death probability.
    - shape: The shape parameter of the Weibull distribution.
    - scale: The scale parameter of the Weibull distribution.
    - life_expectancy: The life expectancy parameter.

    Returns:
    - death_probability: The probability of death at the given age.
    """
    if shape <= 0 or scale <= 0 or life_expectancy <= 0:
        raise ValueError("Shape, scale, and life expectancy must be positive.")

    cdf_at_age = stats.weibull_min.cdf(age, shape, scale=scale)
    cdf_at_life_expectancy = stats.weibull_min.cdf(life_expectancy, shape, scale=scale)
    death_probability = cdf_at_age / cdf_at_life_expectancy

    return death_probability + 1e-4


death_proba = np.zeros(200)
for age in range(0, 200):
    death_proba[age] = death_probability_by_age(age, shape_parameter, scale_parameter, average_life_expectancy)


def simulate_with_fertility_rate(fec_rate=1.2):
    population = np.ones(150)

    for age in range(0, 150):
        p = death_probability_by_age(age, shape_parameter, scale_parameter, average_life_expectancy)
        population[age] = population[age - 1] * (1 - p)

    population *= current_population / sum(population)

    for age in range(0, 150):
        if population[age] < 1:
            population[age] = 0

    # population = population[population > 0]

    ages = list(range(0, 150))

    duration_years = 50
    pops, ratios, immigrations, pension_ages = simulate_model(population=population, fecondity_rate=fec_rate,
                                                              duration_years=duration_years, plot=False,
                                                              debug=True)
    years = list(range(current_year, current_year + duration_years + 1))
    sum_pops = [sum(pop) for pop in pops]

    ratios_vec = np.array([ratio for ratio in ratios]) / ratios[0]

    immigrations_vec = [immigration for immigration in immigrations]

    pension_ages_vec = [age for age in pension_ages]

    return years, pops, sum_pops, ratios_vec, immigrations_vec, pension_ages_vec
