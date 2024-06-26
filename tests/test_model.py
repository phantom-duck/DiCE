import pytest
from rai_test_utils.datasets.tabular import create_iris_data
from raiutils.exceptions import UserConfigValidationException
from sklearn.ensemble import RandomForestClassifier

import custom_dice_ml
from custom_dice_ml.utils import helpers


class TestBaseModelLoader:
    def _get_model(self, backend):
        ML_modelpath = helpers.get_adult_income_modelpath(backend=backend)
        m = custom_dice_ml.Model(model_path=ML_modelpath, backend=backend)
        return m

    def test_tf(self):
        tf = pytest.importorskip("tensorflow")
        backend = 'TF'+tf.__version__[0]
        m = self._get_model(backend)
        assert issubclass(type(m), custom_dice_ml.model_interfaces.base_model.BaseModel)
        assert isinstance(m, custom_dice_ml.model_interfaces.keras_tensorflow_model.KerasTensorFlowModel)

    def test_pyt(self):
        pytest.importorskip("torch")
        backend = 'PYT'
        m = self._get_model(backend)
        assert issubclass(type(m), custom_dice_ml.model_interfaces.base_model.BaseModel)
        assert isinstance(m, custom_dice_ml.model_interfaces.pytorch_model.PyTorchModel)

    def test_sklearn(self):
        pytest.importorskip("sklearn")
        backend = 'sklearn'
        m = self._get_model(backend)
        assert isinstance(m, custom_dice_ml.model_interfaces.base_model.BaseModel)


class TestModelUserValidations:

    def create_sklearn_random_forest_classifier(self, X, y):
        rfc = RandomForestClassifier(n_estimators=10, max_depth=4,
                                     random_state=777)
        model = rfc.fit(X, y)
        return model

    def test_model_user_validation_model_type(self):
        x_train, x_test, y_train, y_test, feature_names, classes = \
            create_iris_data()
        trained_model = self.create_sklearn_random_forest_classifier(x_train, y_train)

        assert custom_dice_ml.Model(model=trained_model, backend='sklearn', model_type='classifier') is not None
        assert custom_dice_ml.Model(model=trained_model, backend='sklearn', model_type='regressor') is not None

        with pytest.raises(UserConfigValidationException):
            custom_dice_ml.Model(model=trained_model, backend='sklearn', model_type='random')

    def test_model_user_validation_no_valid_model(self):
        with pytest.raises(
                ValueError,
                match="should provide either a trained model or the path to a model"):
            custom_dice_ml.Model(backend='sklearn')
