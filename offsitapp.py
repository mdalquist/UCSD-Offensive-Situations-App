import pandas as pd
import numpy as np
import requests as re
import bs4
import streamlit as st

st.title("UC San Diego Offensive Situations Calculator")

st.markdown("Welcome to the UC San Diego Offensive Situations tool! The goal of this app is to provide a quantitative perspective on when to call bunts, steals, or other offensive plays, and evaluate the rate of success needed to increase the probability of scoring one or multiple runs in an inning.")

st.markdown("The first drop down box is to select the team, choose either 'Baseball' or 'Softball'.")

st.markdown('The left and middle columns below are for selecting the base situations and outs before the play, after the play succeeds, and after it fails. The "Goal" box in the right column allows the changing of the calculation based on game situation. For early in the game when scoring multiple runs is important, use the "As Many as Possible" choice. This will calculate the odds based on the average number of runs scored in an inning from that situation. The "One Run" choice is for later in the game, when scoring one run becomes necessary. This choice calculates the odds based on the probability of scoring any amount of runs from that situation. The last selection in the right column is for if any runs are scored during the play. This will be helpful when evaluating squeeze plays.')

st.markdown('Example - Stealing 2nd with no outs:')

st.markdown('>Current situation: runner on 1st 0 outs - 1 _ _, 0 outs')

st.markdown('>Success situation: runner on 2nd 0 outs - _ 2 _, 0 outs')

st.markdown('>Failure situation: bases empty 1 out - _ _ _, 1 outs')

st.markdown('Note that this tool presumes there are only 2 possible outcomes to every play. For a bunt or hit and run, there are obviously more than 2 outcomes. A sac bunt can turn into 1st and 2nd with an error or a double play with a bad bunt, but usually a successful sac means the runner moves up a base and the hitter is out, while a faliure means the hitter gets out without moving up the runner. When using this tool, consider the true goal of the offense and defense on the play, and select the most likely success and failure conditions to get the most accurate results')

st.markdown("Once the situation is set up, you're ready to go! Click the 'Run Situation' button, which will calculate the break even point probability, the probability of success needed to equal the run value of the 'current' situation. The true odds of success will be based on the players involved and the game itself, and can be estimated using the coach's expertise of the game. If the estimated chance of success of the play is greater than the break even point provided by the calculator, running that play would positively impact the run scoring capacity of the offense. If the estimated chance of success is less than the break even point, a success would still improve the offense's run scoring capacity, but the risk outweighs the benefit. If the tool outputs 'Negative run value', the success situation produces fewer expected runs than the current situation, meaning a successful result would not provide the offense any benefit and should not be attempted. This can be counterintuitive at times. For instance, it is obviously better to have a runner on 2nd than 1st, but sometimes there is no difference in the runs scored from the two situations, so there is no benefit to the risk of taking the extra base.")

team = st.selectbox('Team', np.array(['Baseball', 'Softball']))

if team == 'Baseball':
	situations_base = pd.read_csv('baseball_atbats_2021-2023.csv')

if team == 'Softball':
	situations_base = pd.read_csv('softball_atbats_2021-2023.csv')

re_matrix = pd.pivot_table(data = situations_base, values = ['runs_after_batter'], index = ['base'], columns = ['outs'], aggfunc = 'mean')

rp_matrix = pd.pivot_table(data = situations_base, values = ['at_least_1_scored'], index = ['base'], columns = ['outs'], aggfunc = 'mean')

def calc_be_point(current, success, failure, runs = 0, matrix = 're'):
    if matrix == 're':
        s_runs = re_matrix.loc[success['base']].loc['runs_after_batter'].loc[success['outs']] + runs
        c_runs = re_matrix.loc[current['base']].loc['runs_after_batter'].loc[current['outs']]
        if failure['outs'] != 3:
            f_runs = re_matrix.loc[failure['base']].loc['runs_after_batter'].loc[failure['outs']]
        else:
            f_runs = 0
    else:
        if runs == 1:
            s_runs = 1
        else:
            s_runs = rp_matrix.loc[success['base']].loc['at_least_1_scored'].loc[success['outs']]
        c_runs = rp_matrix.loc[current['base']].loc['at_least_1_scored'].loc[current['outs']]
        if failure['outs'] != 3:
            f_runs = rp_matrix.loc[failure['base']].loc['at_least_1_scored'].loc[failure['outs']]
        else:
            f_runs = 0
    risk = c_runs - f_runs
    reward = s_runs - c_runs
    if reward < 0:
        return 'Negative value play'
    break_even = risk / (risk + reward)
    return break_even

col1, col2, col3 = st.columns([1,1,1])

with col1:
	cur_base = st.selectbox('Current Base', np.array(['_ _ _', '1 _ _', '_ 2 _', '_ _ 3', '1 2 _', '1 _ 3', '_ 2 3', '1 2 3']))
	suc_base = st.selectbox('Success Base', np.array(['_ _ _', '1 _ _', '_ 2 _', '_ _ 3', '1 2 _', '1 _ 3', '_ 2 3', '1 2 3']))
	fail_base = st.selectbox('Failure Base', np.array(['_ _ _', '1 _ _', '_ 2 _', '_ _ 3', '1 2 _', '1 _ 3', '_ 2 3', '1 2 3', 'inning over']))

with col2:
	cur_out = st.selectbox('Current Outs', np.array([0, 1, 2]))
	suc_out = st.selectbox('Success Outs', np.array([0, 1, 2]))
	fail_out = st.selectbox('Failure Outs', np.array([0, 1, 2, 3]))

with col3:
	matrix_choice = st.selectbox('Goal', np.array(['As Many as Possible', 'One Run']))
	if matrix_choice == 'One Run':
		runs = st.selectbox('Runs Scored From Success', np.array([0, 1]))
	else:
		runs = st.selectbox('Runs Scored From Success', np.array([0, 1, 2, 3, 4]))

if st.button('Run Situation'):
	if matrix_choice == 'One Run':
		result = calc_be_point({'base': cur_base, 'outs': cur_out}, {'base': suc_base, 'outs': suc_out}, {'base': fail_base, 'outs': fail_out}, runs = runs, matrix = 'rp')
		if isinstance(result,str):
			st.write(result)
			st.write('Scoring Probabilities:')
			col4, col5 = st.columns([1,1])
			with col4:
				st.write(cur_base + ', ' + str(cur_out) + ' out: ' + str(round(rp_matrix.loc[cur_base].loc['at_least_1_scored'].loc[cur_out], 3)))
			with col5:
				st.write(suc_base + ', ' + str(suc_out) + ' out: ' + str(round(rp_matrix.loc[suc_base].loc['at_least_1_scored'].loc[suc_out], 3)))
		else:
			result = round(result, 3) * 100
			st.write("The chance of success needed to break even on scoring probability: " + str(result) + '%')
	else:
		result = calc_be_point({'base': cur_base, 'outs': cur_out}, {'base': suc_base, 'outs': suc_out}, {'base': fail_base, 'outs': fail_out}, runs = runs, matrix = 're')
		if isinstance(result,str):
			st.write(result)
			st.write('Expected Runs:')
			col4, col5 = st.columns([1,1])
			with col4:
				st.write(cur_base + ', ' + str(cur_out) + ' out: ' + str(round(re_matrix.loc[cur_base].loc['runs_after_batter'].loc[cur_out], 3)))
			with col5:
				st.write(suc_base + ', ' + str(suc_out) + ' out: ' + str(round(re_matrix.loc[suc_base].loc['runs_after_batter'].loc[suc_out], 3)))
		else:
			result = round(result, 3) * 100
			st.write("The chance of success needed to break even on expected runs: " + str(result) + '%')