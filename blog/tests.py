from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment
# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_james = User.objects.create_user(username='James', password='somepassword')
        self.user_james.is_staff = True
        self.user_james.save()
        self.user_trump = User.objects.create_user(username='Trump', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_culture = Category.objects.create(name='culture', slug='culture')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        # 포스트(게시물)이 3개 존재하는 경우
        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World!!! We are the world...',
            author=self.user_james,
            category=self.category_programming
        )
        self.post_001.tags.add(self.tag_hello)
        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부가 아니잖아요',
            author=self.user_trump,
            category=self.category_culture
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='세번째 포스트입니다.',
            author=self.user_trump,
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='첫번째 댓글입니다.'
        )

    def navbar_test(self, soup):
        # 네비게이션바가 있다
        navbar = soup.nav
        # 네비게이션바에 Blog, AboutMe라는 문구가 있다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo = navbar.find('a', text='Internet Programming')
        self.assertEqual(logo.attrs['href'], '/')
        home = navbar.find('a', text='Home')
        self.assertEqual(home.attrs['href'], '/')
        blog = navbar.find('a', text='Blog')
        self.assertEqual(blog.attrs['href'], '/blog/')
        about = navbar.find('a', text='About Me')
        self.assertEqual(about.attrs['href'], '/about_me/')

    def category_test(self, soup):
        category = soup.find('div', id='categories-card')
        self.assertIn('Categories', category.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', category.text)
        self.assertIn(f'{self.category_culture.name} ({self.category_culture.post_set.count()})', category.text)
        self.assertIn(f'미분류 (1)', category.text)

    def test_category_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리리 name을 포함하고 있는지
        self.assertIn(self.category_programming.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리리 name을 포함하고 있는지
        self.assertIn(self.tag_hello.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        self.client.login(username='Trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        # 정상적으로 페이지가 로드
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='James', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)

        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Create Post - Blog')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        # input 태그가 있는지 확인
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        # 포스트 생성
        self.client.post('/blog/create_post/',
                         {
                             'title': 'Post form 만들기',
                             'content': "Post form 페이지 만들기",
                             'tags_str': 'new tag; 한글태그, python'
                         })

        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post form 만들기")
        self.assertEqual(last_post.author.username, 'James')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_url = f'/blog/update_post/{self.post_003.pk}/'
        # 로그인하지 않은 경우
        response = self.client.get(update_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_james)
        self.client.login(username='James', password='somepassword')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 403) # 403 : forbidden (접근 권한 금지)

        # 로그인했고 작성자인 경우
        self.client.login(username='Trump', password='somepassword')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

        # 수정 페이지
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Edit Post - Blog')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        # input 태그가 있는지 확인
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        # 실제 수정 후 확인
        response = self.client.post(update_url,
                         {
                             'title': '세번째 포스트 수정',
                             'content': '안녕? 우리는 하나/... 반가와요',
                             'category': self.category_culture.pk,
                             'tags_str': '파이썬 공부; 한글 태그; some tag'
                         }, follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세번째 포스트 수정', main_area.text)
        self.assertIn('안녕? 우리는 하나/... 반가와요', main_area.text)
        self.assertIn(self.category_culture.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_post_list(self):
        # 포스트가 3개 존재하는가
        self.assertEqual(Post.objects.count(), 3)

        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)
        self.category_test(soup)

        # 포스트(게시물)의 타이틀이 3개 존재하는가
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_james.username.upper(), main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)

        # 포스트(게시물)이 하나도 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        # 적절한 안내 문구가 포함되어 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        # 이 포스트의 url이 /blog/1
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1')
        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get('/blog/1', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_test(soup)

        # 포스트의 title은 웹브라우저의 title에 있는가
        self.assertIn(self.post_001.title, soup.title.text)
        # 포스트의 title은 포스트영역에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id="post-area")
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.post_001.category.name, post_area.text)
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        # 포스트 작성자가 있는가
        # 아직 작성중
        # 포스트의 내용이 있는가
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.user_james.username.upper(), post_area.text)

        # comment가 있는 지역이 어디인가
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)