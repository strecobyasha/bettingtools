"""
Get list of games, that

1. Not started;
2. Without preview yet;
3. Should be published within the next 4 hours.

"""

from pathlib import Path

import tensorflow as tf

from camp.preview.collect_games import Collector
from camp.preview.db_manager import DataBaseManager
from camp.preview.predictor import Predictor

path = Path(__file__).resolve().parent.parent
model_address = ''.join([str(path), '/academy/base_model.h5'])

def updater():
    model = tf.keras.models.load_model(model_address)

    collector = Collector()
    predictor = Predictor(model)
    db_manager = DataBaseManager()

    collector.prediction_dataset()

    if not collector.games_data.empty:
        data_set = collector.process_data()
        predictions = predictor.predict_goals(data_set)
        predictions_dict = {prediction['api_game_id']: prediction for prediction in predictions}
        games_to_update = db_manager.get_games_to_update(data_set)
        db_manager.prepare_data(games_to_update, predictions_dict)
        db_manager.update_games(games_to_update)
