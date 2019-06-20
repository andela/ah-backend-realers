from django.test import TestCase
from authors.apps.articles.tests.test_base import ArticleBaseTest
from rest_framework import status
from django.urls import reverse


class ArticleTest(ArticleBaseTest):

    def test_create_article(self):
        self.assertEquals(self.create_new_article.status_code,
                          status.HTTP_201_CREATED)

    def test_create_article_with_existing_body(self):
        response = self.client.post(
            self.article_url,
            self.article_data,
            format='json'
        )
        self.assertIn('Article with this body already exists!',
                      str(response.data))

    def test_create_article_with_invalid_tagname_fails(self):
        self.article_data['article']['tagName'] = "should_a_list"
        self.article_data['article']['body'] = "should_a_list"
        response = self.client.post(
            self.article_url,
            self.article_data,
            format='json'
        )
        self.assertIn('Provide a valid tag list like ',
                      str(response.data))

    def test_get_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

        response = self.client.get(self.article_url)
        slug = self.create_new_article.data["data"]["slug"]
        response2 = self.client.get(self.article_url+f"{slug}/")
        response3 = self.client.get(self.article_url+f"{slug}y/")

        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_delete_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

        slug = self.create_new_article.data["data"]["slug"]
        response = self.client.delete(self.article_url+f"{slug}/")
        response2 = self.client.delete(self.article_url+f"{slug}df/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("success", response.data)

    def test_update_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_article_with_invalid_tagname_fails(self):
        self.article_data['article']['tagName'] = ["should_a_list"]
        self.article_data['article']['body'] = "should_a_list"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data,
            format='json'
        )
        self.assertIn('Tag name should only contain letter',
                      str(response.data))

    def test_update_article_with_non_existant_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good-awesome/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article_with_no_permission(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_article_without_permission(self):
        self.client.credentials()
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_article_fails_with_bad_request_body(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.wrong_request_body,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FavoriteUnfavoriteAnArticleTest(ArticleBaseTest):
    def test_authenticated_user_can_favorite_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        response = self.client.post(
            fav_url
        )
        self.assertEqual(
            "You have favorited this article successfully", response.data.get('message'))

    def tests_unauthenticated_user_cant_favorite_article(self):
        self.client.credentials()
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        response = self.client.post(
            fav_url
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_cant_favorite_article_many_times(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        # below is the first favoriting
        self.client.post(
            fav_url
        )
        # below is the second favoriting
        response = self.client.post(
            fav_url
        )
        self.assertEqual(
            "You favorited this article already", response.data.get('message'))

    def test_authenticated_user_can_unfavorite_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        # here i am first favoriting an article
        self.client.post(
            fav_url
        )
        # then here trying to unfavorite it.
        response = self.client.delete(
            fav_url
        )
        self.assertEqual(
            "This article has been unfavorited successfully", response.data.get('message'))

    def tests_unauthenticated_user_cant_unfavorite_article(self):
        self.client.credentials()
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        response = self.client.delete(
            fav_url
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_cant_unfavorite_article_before_favoriting_it(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        # below is the second favoriting
        response = self.client.delete(
            fav_url
        )
        self.assertEqual(
            "You have not favorited this article yet", response.data.get('message'))

    def test_authenticated_retrieve_all_own_favorite_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        # line below favorite an article
        response = self.client.post(
            fav_url
        )
        # fetch all my favorite articles
        my_fav_articles_url = reverse("articles:favorite_articles")
        response = self.client.get(
            my_fav_articles_url
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            'retrieved all user favorite articles successfully', response.data.get('message'))

    def test_favorited_article_has_favorated_by(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-good"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})
        #favorite article
        self.client.post(
            fav_url
        )
        #retrieve article
        article_url = reverse("articles:slug", kwargs={"slug": slug})
        response = self.client.get(article_url)
        self.assertIn("is_favorited", response.data.get('data'))

    def test_inexistence_article_raises_an_error(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        slug = "most-people-are-goods-non"
        fav_url = reverse("articles:favorite", kwargs={"slug": slug})

        response = self.client.post(
            fav_url
        )

        self.assertEqual(
            "Article doesn't exit", response.data['errors'].get('message'))