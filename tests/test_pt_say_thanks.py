import unittest
from unittest.mock import patch, MagicMock
from src.pt_say_thanks import get_torrent_ids, say_thanks, thank_batch
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('../config/config.env')


def get_config():
    """从 config.env 中读取 headers 和 URL 配置"""

    base_url = f"https://{os.getenv('PT_DOMAIN')}"
    headers = {
        'Cookie': os.getenv('PT_COOKIE'),
        'User-Agent': os.getenv('USER_AGENT'),
        'Referer': base_url
    }
    thanks_url = f"{base_url}/thanks.php"
    return headers, thanks_url


class TestPtSayThanks(unittest.TestCase):

    @patch('src.pt_say_thanks.requests.get')
    def test_get_torrent_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<a href="details.php?id=123&amp;hit=1"></a><a href="details.php?id=456&amp;hit=1"></a>'
        mock_get.return_value = mock_response

        headers = {'User-Agent': 'test-agent'}
        torrent_ids = get_torrent_ids('https://example.com?page=1', headers)

        self.assertEqual(torrent_ids, {'123', '456'})
        mock_get.assert_called_once_with('https://example.com?page=1', headers=headers, timeout=60)

    @patch('src.pt_say_thanks.requests.post')
    def test_say_thanks_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        headers = {'User-Agent': 'test-agent'}
        success = say_thanks('123', 1, 'https://example.com/thanks.php', headers)

        self.assertTrue(success)
        mock_post.assert_called_once_with(
            'https://example.com/thanks.php',
            headers=headers,
            data={'id': '123'},
            timeout=60
        )

    @patch('src.pt_say_thanks.requests.post')
    def test_say_thanks_failure(self, mock_post):
        mock_post.side_effect = Exception("Request failed")

        headers = {'User-Agent': 'test-agent'}
        success = say_thanks('123', 1, 'https://example.com/thanks.php', headers)

        self.assertFalse(success)

    @patch('src.pt_say_thanks.say_thanks')
    def test_thank_batch(self, mock_say_thanks):
        mock_say_thanks.side_effect = [True, False, True]

        headers = {'User-Agent': 'test-agent'}
        all_torrent_ids = {'123', '456', '789'}
        failed_ids = {'456'}

        with patch('src.pt_say_thanks.logger') as mock_logger:
            thank_batch(all_torrent_ids, headers, 'https://example.com/thanks.php')

            self.assertEqual(mock_say_thanks.call_count, 3)
            mock_logger.warning.assert_called_with(f"以下种子感谢失败: {failed_ids}")

    def test_retry_failed_torrent_ids(self):
        """测试重试失败的种子ID，可以把失败的种子ID传递给 thank_batch 函数"""

        # 种子 ID set
        torrent_ids = {'33354', '33353'}
        headers, thanks_url = get_config()

        # 重试失败的种子ID
        thank_batch(torrent_ids, headers, thanks_url)


if __name__ == '__main__':
    unittest.main()
