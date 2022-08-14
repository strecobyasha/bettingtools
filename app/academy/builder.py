"""
Prediction model builder.
"""

import warnings

import numpy as np
import tensorflow as tf
from tabulate import tabulate
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam

from academy.model_test import test
from camp.preview.collect_games import Collector
from camp.preview.predictor import Predictor


def start():
    warnings.filterwarnings('ignore')
    np.random.seed(5)           # Create the same train, test and check datasets every time.
    tf.random.set_seed(5)       # Get the same learning result when model params do not change.

    # Collect data from DB.
    collector = Collector()
    collector.learning_dataset()
    data_set = collector.process_data()

    # Create datasets.
    train_dataset = data_set.sample(frac=0.7)
    test_dataset = data_set.drop(train_dataset.index).sample(frac=0.7)
    check_dataset = data_set.drop(train_dataset.index).drop(test_dataset.index).sample(frac=1)

    x_train, y_train = Predictor.prepare_data(train_dataset, test=True)
    x_test, y_test = Predictor.prepare_data(test_dataset, test=True)
    print(x_train.shape)
    print(x_test.shape)

    # Build custom model.
    cstm_model = build_model(x_train, y_train, x_test, y_test)
    # cstm_model.save('./academy/base_model.h5')

    # Test model
    ests = {'CSTM': cstm_model}
    tab = []

    for name, model in ests.items():
        bets = test(model, check_dataset)
        tab.append(
            [
                name,
                bets['outcome_bets'],
                f"{bets['outcome_wins']} ({round(bets['outcome_wins']*100/bets['outcome_bets'], 2)}%)",
                f"{round(bets['outcome_profit'], 2)} ({round(bets['outcome_profit']*100/bets['outcome_bets'], 1)}%)",
                bets['home_win_preds'],
                bets['draw_preds'],
                bets['away_win_preds'],
                bets['total_bets'],
                f"{bets['total_wins']} ({round(bets['total_wins'] * 100 / bets['total_bets'], 2)}%)",
                f"{round(bets['total_profit'], 2)} ({round(bets['total_profit'] * 100 / bets['total_bets'], 1)}%)",
                bets['total_under_preds'],
                bets['total_over_preds'],
                f"{bets['home_goals_pred']} / {bets['home_goals_act']}",
                f"{bets['away_goals_pred']} / {bets['away_goals_act']}",
            ]
        )

    # Show result for all models.
    sorted_tab = sorted(tab, key=lambda x: float(x[3][:x[3].index(' (')]), reverse=True)
    print(
        tabulate(
            sorted_tab,
            headers=['Model', 'Outcome bets', 'Outcome Wins', 'Outcome Profit',
                     'HWP', 'DP', 'AWP', 'Total bets', 'Total Wins', 'Total Profit',
                     'TU', 'TO', 'HG', 'AG'],
            tablefmt='pretty')
        )


def build_model(x_train, y_train, x_test, y_test):
    # normalizer = preprocessing.Normalization()
    # normalizer.adapt(np.array(x_train))
    predict_model = models.Sequential()
    # predict_model.add(normalizer)
    predict_model.add(layers.Dense(
        243, activation='relu', kernel_initializer='he_uniform', input_shape=(3,))
        )
    predict_model.add(layers.Dropout(0.1))
    predict_model.add(layers.Dense(27, activation='relu'))
    predict_model.add(layers.Dropout(0.1))
    predict_model.add(layers.Dense(3, activation='relu'))
    predict_model.add(layers.Dense(1, activation='relu'))
    opt = Adam(learning_rate=0.001)
    predict_model.compile(loss='mean_squared_error', optimizer=opt, metrics=['mae'])
    
    predict_model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        epochs=40,
        batch_size=10000,
        )
    
    return predict_model
