from aws_cdk import SecretValue
from constructs import Construct

class SecretConfigJson:
    """Provide easy access to the JSON keys stored in a SecretsManager JSON document."""
    def __init__(self, secret_id):
        self.secret_id = secret_id

    def _get_secret_value(self, json_field: str) -> SecretValue:
        return SecretValue.secrets_manager(self.secret_id, json_field=json_field)

    @property
    def codestar_connection_arn(self) -> SecretValue:
        """For Pipeline Stack

        :return: Value defined at the JSON key "codestar_connection_arn"
        :rtype: SecretValue
        """
        return self._get_secret_value("codestar_connection_arn")


class SecretConfigStackMixin:
    """Mixin that allows a stack to get secret values from a JSON config
    uploaded to the configured SecretsManager secret ID.
    """

    SECRET_CONFIG_SECRET_ID_CDK_CONTEXT_VARIABLE = (
        "control-broker/secret-config/secrets-manager-secret-id"
    )

    __secrets: SecretConfigJson = None

    @property
    def secrets(self: Construct):
        """Access JSON keys in the JSON doc at the secret ID specified by SECRET_CONFIG_SECRET_ID_CDK_CONTEXT_VARIABLE

        :return: Object whose attributes are those of the JSON document of the secret.
        :rtype: SecretManagerJson
        """
        if self.__secrets is None:
            secret_id = self.node.try_get_context(self.SECRET_CONFIG_SECRET_ID_CDK_CONTEXT_VARIABLE)
            self.__secrets = SecretConfigJson(secret_id)
        return self.__secrets