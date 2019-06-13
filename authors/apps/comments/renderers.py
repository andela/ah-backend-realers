import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList

class CommentJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        try:
            data['errors']
        except:
            # if errors is None:
            return super(CommentJSONRenderer, self).render(data)

        return json.dumps({
            "coments": data
        })
