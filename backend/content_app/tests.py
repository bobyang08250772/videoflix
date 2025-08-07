from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from content_app.models import Video
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class HLSViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@example.com', email='test@example.com', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.video = Video.objects.create(title='Sample Video', video_file='videos/sample.mp4') 
    
    def test_video_list_view_authenticated(self):
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        titles = [video['title'] for video in response.data]
        self.assertIn('Sample Video', titles)

    def test_video_list_view_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", create=True)
    def test_hls_playlist_view_success(self, mock_open, mock_exists):
        url = reverse('HSL-playlist', kwargs={'pk': self.video.id, 'resolution': '720p'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')

    @patch("os.path.exists", return_value=False)
    def test_hls_playlist_view_file_not_found(self, mock_exists):
        url = reverse('HSL-playlist', kwargs={'pk': self.video.id, 'resolution': '720p'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_hls_playlist_video_not_found(self):
        url = reverse('HSL-playlist', kwargs={'pk': 999, 'resolution': '720p'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
