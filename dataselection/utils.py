from itertools import combinations
from scipy.stats import norm

def cols_list_combinations_generator(cols_to_combinate , col_to_append_at_end):
    """Generates from a list of columns, all combinations of them, where order is irrelevant, and where combinations can have missing cols. Finally , it's added a column name at end of all combinations.
    
    
    :param cols_to_combinate: list of columns to make combinations prior to concatenation
    :param col_to_append_at_end: col to append at end to every combination
    
    >>>cols_list_combinations_generator(["col1","col2"],"col3")
    [['col1', 'max_margin_improve'],
     ['col2', 'max_margin_improve'],
     ['col1', 'col2', 'max_margin_improve']]    
    """    
    lista_combinaciones = []

    for r in range(1, len(cols_to_combinate) + 1):
        for comb in combinations(cols_to_combinate, r):
            lista_a_agregar = list(comb)
            lista_a_agregar.append(col_to_append_at_end)
            lista_combinaciones.append(lista_a_agregar)

    return lista_combinaciones


def calculate_small_bernoulli_sample_size(pop=500*1000, eps=0.05, p=0.5, confidence=0.95):
    """Calculates the minimum sample size to be statistically significant a sample to a bernoulli population (even a small one)
    
    
    :param pop: number of members of all population
    :param eps: epsilon or margin of error to use to calculate statistical significant sample size
    :param p: proportion of 1's in all population. If unknown, use max variance : p=0.5
    :param confidence: confidence to use to calculate statistical significant sample size


    >>>calculate_small_bernoulli_sample_size(pop=1000, eps=0.01, p=0.02, confidence=0.95)
    430 
    """
    if p - eps < 0:
        raise ValueError("Error: Invalid input values. The margin of error (eps) cannot be greater than the proportion (p) with this formula. Please provide valid input values.")

    z = norm.ppf(1 - (1 - confidence) / 2)  # Critical value corresponding to the confidence level
    sample_size = ( z**2 * p * (1 - p) * pop ) / ( (eps**2 * pop) + (z**2 * p * (1 - p)) )
    
    # Round sample size up to the nearest integer
    sample_size = int(round(sample_size))
    
    return sample_size

def relevant_grp_extractor(df,error_exagerator_factor,columns_that_make_groups,relevant_groups_dict ):
    """Extracts in dict of dicts all col_combinations-values with statistical signficance and with more one's that general avg.
    
    
    :param df: dataframe where all groups , with signfificance or not
    :param error_exagerator_factor: factor to re-size (make bigger) the proportions of 1's , for better use in calculate_small_bernoulli_sample_size
    :param columns_that_make_groups: columns of df, on wich groups are made
    :param relevant_groups_dict: dict where significants groups are saved
    """
    df['error_perc']= df['sampled_w_error']/df['sampled_pop']
    df['exagerated_error'] = df['error_perc'].apply(lambda x: min(error_exagerator_factor*x, 0.5))  # Exagerates error but closer to reality than max variance 
    df['min_sample'] = df.apply(lambda row: calculate_small_bernoulli_sample_size(pop= row['total_population'], p= row['exagerated_error'] , eps=0.05 )  , axis=1 )    

    # Selecciono el df de grupos representativos

    representative_df= df[df["sampled_pop"]>=df["min_sample"]] 

    # Calculo el error global

    total_sampled_w_error= sum(df["sampled_w_error"])
    total_sampled= sum(df["sampled_pop"])
    total_error= total_sampled_w_error / total_sampled 

    # Filtro las filas que tienen un mayor error que el promedio general

    representative_df_w_gain= representative_df[representative_df["error_perc"]>=total_error]
    representative_df_w_gain["error_without_grp"]= (total_sampled_w_error- representative_df_w_gain["sampled_w_error"] )/total_sampled
    representative_df_w_gain["max_margin_improve"]= total_error - representative_df_w_gain["error_without_grp"] 

    columns_to_drop = set(representative_df_w_gain.columns) - set(columns_that_make_groups)
    extract_groups_df = representative_df_w_gain.drop(columns=columns_to_drop)
    extract_groups_df= extract_groups_df.reset_index(drop=True)
    
    if len(relevant_groups_dict) > 0:
        max_num = max([int(key.split('_')[1]) for key in relevant_groups_dict.keys()])
    else:
        max_num = 0

    # Concatenar cada línea del DataFrame en el diccionario existente con etiquetas únicas
    for index, row in extract_groups_df.iterrows():
        inner_dict = row.to_dict()
        dict_key = f'grp_{max_num + index + 1}'  # Etiqueta única numerada posteriormente
        relevant_groups_dict[dict_key] = inner_dict
    return relevant_groups_dict