from .test_base import TestBase
import json
from rest_framework import status
from ..models import Comment


class CommentsTests(TestBase):

    def test_create_comment(self):
        url = self.article_url+f"{self.article_slug}/comments/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.post(
            url,
            data=self.comment_data,
            format='json'
            )
        expected = "we dem' boys, Holla"

        self.assertEqual(expected, response.data['comment']['body'])

    def test_create_comment_no_comment_in_data(self):
        url = self.article_url+f"{self.article_slug}/comments/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.post(
            url,
            data=self.request_data_no_comment,
            format='json'
            )
        expected = "There is no comment in the request data"

        self.assertEqual(expected, response.data['error'])

    def test_create_comment_no_body_in_comment(self):
        url = self.article_url+f"{self.article_slug}/comments/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.post(
            url,
            data=self.comment_data_no_body,
            format='json'
            )
        expected = "The comment body must be provided"

        self.assertEqual(expected, response.data['error'])

    def test_create_comment_article_invalid(self):
        url = self.article_url+"baby/comments/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.post(
            url,
            data=self.comment_data,
            format='json'
            )
        expected = "Article not found"

        self.assertEqual(expected, response.data['errors'][0])

    def test_delete_comment(self):
        delete_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        response = self.client.delete(
            delete_url
        )
        expected = "Comment successfully deleted"

        self.assertEqual(expected, response.data['message'])

    def test_delete_comment_not_yours(self):
        delete_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token2))
        response = self.client.delete(
            delete_url
        )
        expected = "Users can only delete their own comments"

        self.assertEqual(expected, response.data['error'])

    def test_edit_comment(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        response=self.client.patch(
            edit_url,
            data=self.comment_data,
            format='json'
            )
        expected = "Comment successfully updated"

        self.assertEqual(expected, response.data['message'])

    def test_edit_comment_not_yours(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token2))
        response=self.client.patch(
            edit_url,
            data=self.comment_data,
            format='json'
            )
        expected = "You can't edit someone else's comment"

        self.assertEqual(expected, response.data['error'])

    def test_get_a_comment(self):
        get_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        response=self.client.get(
            get_url
            )
        expected = "we dem' boys, Holla"

        self.assertEqual(expected, response.data[0]['body'])

    def test_get_a_comment_article_invalid(self):
        get_url = self.article_url+f"baby/comments/{self.comment_id}"
        response=self.client.get(
            get_url
            )
        expected = "Article not found"

        self.assertEqual(expected, response.data['errors'][0])

    def test_get_a_comment_invalid_id(self):
        get_url = self.article_url+f"{self.article_slug}/comments/67"
        response=self.client.get(
            get_url
            )
        expected = "Comment not found"

        self.assertEqual(expected, response.data['error'])

    def test_get_a_comment_bad_id(self):
        get_url = self.article_url+f"{self.article_slug}/comments/dwdw"
        response=self.client.get(
            get_url
            )
        expected = "Comment id must be an integer"

        self.assertEqual(expected, response.data['error'])

    def test_get_all_comments(self):
        url = self.article_url+f"{self.article_slug}/comments/"
        response=self.client.get(
            url
            )
        expected = "we dem' boys, Holla"

        self.assertEqual(expected, response.data[0]['body'])

    def test_get_all_comments_none_yet(self):
        url = self.article_url+f"{self.article_slug2}/comments/"
        response=self.client.get(
            url
            )
        expected = "No comments on this article yet"

        self.assertEqual(expected, response.data['error'])

    def test_model_class_stringify(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        comment = Comment.objects.first()

        self.assertEqual(str(comment), comment.body)



    def test_edit_comment_no_comment_in_request(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        response=self.client.patch(
            edit_url,
            data=self.request_data_no_comment,
            format='json'
            )
        expected = "There is no comment in the request data"

        self.assertEqual(expected, response.data['error'])

    def test_edit_comment_no_body_in_comment(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/{self.comment_id}"
        response=self.client.patch(
            edit_url,
            data=self.comment_data_no_body,
            format='json'
            )
        expected = "The comment body must be provided"

        self.assertEqual(expected, response.data['error'])

    def test_edit_comment_not_exist(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/40"
        response=self.client.patch(
            edit_url,
            data=self.comment_data_no_body,
            format='json'
            )
        expected = "Comment not found"

        self.assertEqual(expected, response.data['error'])

    def test_edit_comment_bad_id(self):
        edit_url = self.article_url+f"{self.article_slug}/comments/dw"
        response=self.client.patch(
            edit_url,
            data=self.comment_data_no_body,
            format='json'
            )
        expected = "Comment id must be an integer"

        self.assertEqual(expected, response.data['error'])

    def test_delete_comment_not_exist(self):
        delete_url = self.article_url+f"{self.article_slug}/comments/40"
        response = self.client.delete(
            delete_url
        )
        expected = "Comment not found"

        self.assertEqual(expected, response.data['error'])

    def test_delete_comment_bad_id(self):
        delete_url = self.article_url+f"{self.article_slug}/comments/tr"
        response = self.client.delete(
            delete_url
        )
        expected = "Comment id must be an integer"

        self.assertEqual(expected, response.data['error'])
