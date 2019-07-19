import sys
import os
import numpy as np
import pandas as pd
import sklearn as sk
from collections import defaultdict, Counter
from sklearn.model_selection import train_test_split
import xgboost as xgb


# The first step is 
# to get our machine learning dataset:
# 


def logic_layer(x):

	# preparation_steps = []
	# preparation_output_schema = {u'userModified': False, u'columns': [{u'type': u'bigint', u'name': u'year'}, {u'type': u'bigint', u'name': u'quarter'}, {u'type': u'bigint', u'name': u'market'}, {u'type': u'bigint', u'name': u'dur_stay'}, {u'type': u'bigint', u'name': u'mode'}, {u'type': u'bigint', u'name': u'purpose'}, {u'type': u'double', u'name': u'Visits (000s)'}, {u'type': u'double', u'name': u'Spend (\xa3m)'}]}

	workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in

	ml_dataset_handle = pd.read_csv(os.path.join(workpath, 'data_2014_2017_prepared.csv'))
	# ml_dataset_handle.set_preparation_steps(preparation_steps, preparation_output_schema)
	ml_dataset = ml_dataset_handle

	# print ('Base data has %i rows and %i columns' % (ml_dataset.shape[0], ml_dataset.shape[1]))
	# Five first records",
	# ml_dataset.head(5)





	ml_dataset = ml_dataset[[u'quarter', u'Visits (000s)', u'mode', u'purpose', u'year', u'dur_stay', u'market', u'Spend (\xa3m)']]



	ml_dataset['__target__'] = ml_dataset['Visits (000s)']
	del ml_dataset['Visits (000s)']


	# Remove rows for which the target is unknown.
	ml_dataset = ml_dataset[~ml_dataset['__target__'].isnull()]



	def coerce_to_unicode(x):
		if sys.version_info < (3, 0):
			if isinstance(x, str):
				return unicode(x,'utf-8')
			else:
				return unicode(x)
		else:
			return str(x)


	a = pd.DataFrame(columns = ['quarter', 'mode','purpose','year','dur_stay','market', 'Spend (£m)', '__target__'])
	a.loc[0]= x



	# train, test = train_test_split(ml_dataset, test_size=0.0)
	train = ml_dataset
	test = a
	# print ('Train data has %i rows and %i columns' % (train.shape[0], train.shape[1]))
	# print ('Test data has %i rows and %i columns' % (test.shape[0], test.shape[1]))
	# train = ml_dataset



	drop_rows_when_missing = []
	impute_when_missing = [{'impute_with': u'MEAN', 'feature': u'quarter'}, {'impute_with': u'MEAN', 'feature': u'mode'}, {'impute_with': u'MEAN', 'feature': u'purpose'}, {'impute_with': u'MEAN', 'feature': u'year'}, {'impute_with': u'MEAN', 'feature': u'dur_stay'}, {'impute_with': u'MEAN', 'feature': u'market'}, {'impute_with': u'MEAN', 'feature': u'Spend (\xa3m)'}]

	# Features for which we drop rows with missing values"
	for feature in drop_rows_when_missing:
		train = train[train[feature].notnull()]
		test = test[test[feature].notnull()]
	#     print ('Dropped missing records in %s' % feature)

	# Features for which we impute missing values"
	for feature in impute_when_missing:
		if feature['impute_with'] == 'MEAN':
			v = train[feature['feature']].mean()
		elif feature['impute_with'] == 'MEDIAN':
			v = train[feature['feature']].median()
		elif feature['impute_with'] == 'CREATE_CATEGORY':
			v = 'NULL_CATEGORY'
		elif feature['impute_with'] == 'MODE':
			v = train[feature['feature']].value_counts().index[0]
		elif feature['impute_with'] == 'CONSTANT':
			v = feature['value']
		train[feature['feature']] = train[feature['feature']].fillna(v)
		test[feature['feature']] = test[feature['feature']].fillna(v)
	#     print ('Imputed missing values in feature %s with value %s' % (feature['feature'], coerce_to_unicode(v)))




	rescale_features = {u'dur_stay': u'AVGSTD', u'mode': u'AVGSTD', u'Spend (\xa3m)': u'AVGSTD', u'year': u'AVGSTD', u'quarter': u'AVGSTD', u'market': u'AVGSTD', u'purpose': u'AVGSTD'}
	for (feature_name, rescale_method) in rescale_features.items():
		if rescale_method == 'MINMAX':
			_min = train[feature_name].min()
			_max = train[feature_name].max()
			scale = _max - _min
			shift = _min
		else:
			shift = train[feature_name].mean()
			scale = train[feature_name].std()
		if scale == 0.:
			del train[feature_name]
			del test[feature_name]
	#         print ('Feature %s was dropped because it has no variance' % feature_name)
		else:
	#         print ('Rescaled %s' % feature_name)
			train[feature_name] = (train[feature_name] - shift).astype(np.float64) / scale
			test[feature_name] = (test[feature_name] - shift).astype(np.float64) / scale



	train_X = train.drop('__target__', axis=1)
	test_X = test.drop('__target__', axis=1)

	train_Y = np.array(train['__target__'])
	test_Y = np.array(test['__target__'])

	clf = xgb.XGBRegressor(
						max_depth=10,
						learning_rate=0.1,
						gamma=0.0,
						min_child_weight=0.0,
						max_delta_step=0.0,
						subsample=1.0,
						colsample_bytree=0.75,
						colsample_bylevel=1.0,
						reg_alpha=0.0,
						reg_lambda=1.0,
						n_estimators=300,
						silent=0,
						nthread=4,
						scale_pos_weight=1.0,
						base_score=0.5,
						seed=1337,
						missing=None,
					  )



	# %time 
	clf.fit(train_X, train_Y)



	# a = pd.DataFrame(columns = ['quarter', 'mode','purpose','year','dur_stay','market', 'Spend (£m)'])




	# a['quarter'] = -1.380899
	# a['mode'] = -0.638146
	# a['purpose'] = 1.315741
	# a['year'] = -1.325480
	# a['dur_stay'] = -0.231486
	# a['market'] = 0.081364
	# a['Spend (£m)'] = -0.319305


	# x = [-1.380899, -0.638146, 1.315741, -1.325480, -0.231486, 0.081364, -0.319305]



	_predictions = clf.predict(test_X)
	predictions = pd.Series(data=_predictions, index=test_X.index, name='predicted_value')
	return int(round(predictions * 1000))


	
	
if __name__ == "__main__":
	x = [-1.380899, -0.638146, 1.315741, -1.325480, -0.231486, 0.081364, -0.319305, 0.380]
	y = [3, 3, 2, 2016, 7, 5, 0.897155, 3.556813]
	print(logic_layer(y))
	input()