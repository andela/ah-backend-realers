from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions
from authors.apps.article_tagging.models import ArticleTagging
from authors.apps.article_tagging.serializers import ArticleTaggingSerializer
import re
# Create your views here.


class ArticleTaggingViewSet(ModelViewSet):

    queryset = ArticleTagging.objects.all()
    serializer_class = ArticleTaggingSerializer
    
    def validate_tag_list(self,provided_tags = []):
        try:
            if type(provided_tags) is list: 
                tags = {tag.lower() for tag in provided_tags}
                return tags
            raise exceptions.ValidationError
        except exceptions.ValidationError:
            raise exceptions.ValidationError(
                            'Provide a valid tag list like [\"tag2\",\"tag2\"]')   

    def validate_tag(self,field):

        if re.search(r'^[A-Za-z]+$', field) is None:
            raise exceptions.ValidationError(
                'Tag name should only contain letter'
            )         

    def create_tag_if_provided_is_inexistent(self, provided_tags):
        
        tag_list = self.validate_tag_list(ArticleTaggingViewSet,provided_tags)
        for this_tag in tag_list:
            self.validate_tag(ArticleTaggingViewSet,this_tag)
            try:
                ArticleTagging.objects.get(tag_name=this_tag)
            except ObjectDoesNotExist:
                serializer = ArticleTaggingSerializer(
                    data={'tag_name': this_tag}
                )
                serializer.is_valid(serializer)
                self.perform_create(ArticleTaggingViewSet, serializer)
        return tag_list

