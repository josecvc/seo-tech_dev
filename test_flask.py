import unittest

from flask_testing import TestCase
from flask_server import *
from flask_login import FlaskLoginClient

class MyTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    TESTING = True

    def create_app(self):
        app.test_client_class = FlaskLoginClient
        self.client=app.test_client()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def create_dummy_game(self):
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
        return game
        
    def create_dummy_user(self):
        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123",
            create_date = datetime(2023, 3, 15, 0, 0, 0, 0)
        )

        db.session.add(user)
        db.session.commit()
        return user
    
    def create_dummy_collection(self, user:User):
        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        collection = Collection (
            user_id = user.id,
            name="test",
            public=True,
            desc="Collection",
            created=date,
            updated=date,
        )

        db.session.add(collection)
        db.session.commit()

        return collection

class TestDBAddition(MyTest):
    def test_user_added(self):

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )
        db.session.add(user)
        db.session.commit()

        assert user in db.session

    def test_game_added(self):
        # create date object
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()

        assert game in db.session

    def test_developer_added(self):
        
        dev = Developer (
            rawgid=123,
            name="test"
        )
        db.session.add(dev)
        db.session.commit()

        assert dev in db.session
    
    def test_publisher_added(self):
        
        pub = Publisher (
            rawgid=123,
            name="test"
        )
        db.session.add(pub)
        db.session.commit()

        assert pub in db.session

    def test_genre_added(self):
        
        gen = Genre (
            rawgid=123,
            name="test"
        )
        db.session.add(gen)
        db.session.commit()

        assert gen in db.session
    
    def test_platform_added(self):
        plat = Platform (
            rawgid=123,
            name="test"
        )

        db.session.add(plat)
        db.session.commit()

        assert plat in db.session
    
    def test_collection_added(self):

        # create dummy user

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        collection = Collection (
            user_id = user.id,
            name="test",
            public=True,
            desc="Collection",
            created=date,
            updated=date,
        )

        db.session.add(collection)
        db.session.commit()

        assert collection in db.session

    def test_frag_added(self):

        # create dummy user

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        frag = Frag (
            user_id = user.id,
            game_id = game.id,
            time_played = 3600,
            last_played = date,
            is_currently_playing = False
        )
        db.session.add(frag)
        db.session.commit()

        assert frag in db.session
    
    def test_rating_added(self):

        # create dummy user

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        rating = Rating (
            user_id = user.id,
            game_id = game.id,
            rating = 5,
            timestamp = date,
            review = "Test"
        )
        db.session.add(rating)
        db.session.commit()

        assert rating in db.session

class TestDBLinks(MyTest):
    def test_user_frags(self):

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        frag = Frag (
            user_id = user.id,
            game_id = game.id,
            time_played = 3600,
            last_played = date,
            is_currently_playing = False
        )
        db.session.add(frag)
        db.session.commit()

        assert user == frag.user

    def test_game_frags(self):

        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        frag = Frag (
            user_id = user.id,
            game_id = game.id,
            time_played = 3600,
            last_played = date,
            is_currently_playing = False
        )
        db.session.add(frag)
        db.session.commit()

        assert game == frag.game
    
    def test_game_collections(self):
        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        collection = Collection (
            user_id = user.id,
            name="test",
            public=True,
            desc="Collection",
            created=date,
            updated=date,
        )

        db.session.add(collection)
        db.session.commit()

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )

        collection.games.append(game)

        db.session.add(game)
        db.session.commit()


        assert game in collection.games
    
    def test_user_ratings(self):
        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        rating = Rating (
            user_id = user.id,
            game_id = game.id,
            rating = 5,
            timestamp = date,
            review = "Test"
        )
        db.session.add(rating)
        db.session.commit()

        assert user == rating.user
    
    def test_game_ratings(self):
        user = User(
            username="test_user",
            email="test@address.com",
            password="hello123"
        )

        db.session.add(user)
        db.session.commit()

        # create dummy game

        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()
    
        # create date

        date = datetime(2023, 1, 1, 0, 0, 0, 0)

        rating = Rating (
            user_id = user.id,
            game_id = game.id,
            rating = 5,
            timestamp = date,
            review = "Test"
        )
        db.session.add(rating)
        db.session.commit()

        assert game == rating.game

    def test_game_genres(self):
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()

        gen = Genre (
            rawgid=123,
            name="test"
        )
        game.genres.append(gen)

        db.session.add(gen)
        db.session.commit()

        assert gen in game.genres

    def test_game_platforms(self):
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()

        plat = Platform (
            rawgid=123,
            name="test"
        )
        game.platforms.append(plat)

        db.session.add(plat)
        db.session.commit()

        assert plat in game.platforms

    def test_game_publishers(self):
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()

        pub = Publisher (
            rawgid=123,
            name="test"
        )
        game.publishers.append(pub)

        db.session.add(pub)
        db.session.commit()

        assert pub in game.publishers

    def test_game_developers(self):
        date = datetime(1970, 1, 1).date()
        game = Game (
            rawgid=123,
            title="game",
            desc="game desc",
            image="image.jpg",
            background="bg.jpg",
            metacritic=100,
            released=date,
            website="website.com"
        )
        db.session.add(game)
        db.session.commit()

        dev = Developer (
            rawgid=123,
            name="test"
        )
        game.developers.append(dev)

        db.session.add(dev)
        db.session.commit()

        assert dev in game.developers

class TestViews(MyTest):
    render_templates = False

    def test_some_json(self):
        response = self.client.get("/test/")
        self.assertEqual(response.json, dict(success=True))

    def test_render_register(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
    
    def test_render_login(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
    
    def test_render_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_render_games(self):
        response = self.client.get(f"/games/")
        self.assertEqual(response.status_code, 200)

    def test_render_game(self):
        game = self.create_dummy_game()
        response = self.client.get(f"/games/{game.id}/")
        self.assertEqual(response.status_code, 200)
    
    def test_render_user(self):
        user = self.create_dummy_user()
        response = self.client.get(f"/user/{user.username}/")
        self.assertEqual(response.status_code, 200)

    def test_render_user_collections(self):
        user = self.create_dummy_user()
        response = self.client.get(f"/user/{user.username}/collections/")
        self.assertEqual(response.status_code, 200)

    def test_render_collection(self):
        user = self.create_dummy_user()
        coll = self.create_dummy_collection(user)
        response = self.client.get(f"/user/{user.username}/collections/{coll.id}/")
        self.assertEqual(response.status_code, 200)

class TestAuth(MyTest):
    def register(self, username, email, password):
        return self.client.post('/register/',
                            data=dict(
                                username=username,
                                email=email,
                                password=password, 
                                confirm=password),
                                follow_redirects=True
                            )
    
    def login(self, username, password):
        return self.client.post("/login/",
                            data=dict(
                                username=username,
                                password=password
                                ))
    # Without using flask-login
    def test_valid_user_registration(self):
        response = self.register('test', 'test@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
    
    def test_valid_user_login(self):
        self.register('test', 'test@example.com', 'password123')
        response = self.login("test", "password123")
        self.assertEqual(response.status_code, 200)

    # With flask-login
    def test_homepage_with_logged_in_user(self):
        user = self.create_dummy_user()
        with app.test_client(user=user) as client:
            # This request has user 1 already logged in!
            response = client.get("/home/")
            self.assertEqual(response.status_code, 200)
    
    def test_homepage_anonymous(self):
        # Redirect to login page
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        # Logout and redirect to home page
        user = self.create_dummy_user()
        with app.test_client(user=user) as client:
            response = client.post(url_for('logout'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
    

    
class TestAddition(MyTest):
    def test_add_frag(self):
        user = self.create_dummy_user()
        
        with app.test_client(user=user) as client:
            game = self.create_dummy_game()

            response = client.post("/addfrag", json=dict(
                                user_id = user.id,
                                game_id = game.id,
                                datestamp="2023-06-12",
                                timestamp="0:00",
                                time_played = 3600,
                                unit="Seconds"),
                                follow_redirects=True)
            self.assertEqual(response.status_code, 201)

    def test_add_collection(self):
        user = self.create_dummy_user()
        
        date = datetime(2023, 6, 12, 0, 0, 0, 0)

        with app.test_client(user=user) as client:
            response = client.post(f'/user/{user.username}/collections/',
                                data=dict(
                                    collection_name="test",
                                    desc="test desc",
                                    public=True, 
                                    created=date,
                                    updated=date),
                                    follow_redirects=True
                                )
            self.assertEqual(response.status_code, 200)

    def test_add_game_to_collection(self):
        user = self.create_dummy_user()
        collection = self.create_dummy_collection(user)
        game = self.create_dummy_game()

        with app.test_client(user=user) as client:
            response = client.post("/addtocollection", json=dict(
                                collection_id = collection.id,
                                game_id = game.id), 
                                follow_redirects=True
                                )
            self.assertEqual(response.status_code, 201)
    
    def test_add_rating(self):
        user = self.create_dummy_user()
        game = self.create_dummy_game()

        with app.test_client(user=user) as client:
            response = client.post("/addrating", json=dict(
                                game_id = game.id,
                                rating = 5,
                                review="test"), 
                                follow_redirects=True
                                )
            self.assertEqual(response.status_code, 201)

class TestRAWGAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass
    
    async def asyncSetUp(self):
        self._async_connection:aiohttp.ClientSession = aiohttp.ClientSession()

    async def test_get_data(self):
        '''Function retrieves game data from the API'''
        response = await self._async_connection.get(f"https://api.rawg.io/api/games?key={RAWG_KEY}&page_size=5")
                
        self.assertEqual(response.status, 200)
        response.close()
        self.addAsyncCleanup(self.on_cleanup)
    
    def tearDown(self):
        pass
    
    async def asyncTearDown(self):
        await self._async_connection.close()
    
    async def on_cleanup(self):
        pass

class TestSteamUserInfoAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass
    
    async def asyncSetUp(self):
        self._async_connection:aiohttp.ClientSession = aiohttp.ClientSession()

    async def test_get_data(self):
        '''Function retrieves game data from the API'''
        response = await self._async_connection.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API}&steamids=76561198119238820")
                
        self.assertEqual(response.status, 200)
        response.close()
        self.addAsyncCleanup(self.on_cleanup)
    
    def tearDown(self):
        pass
    
    async def asyncTearDown(self):
        await self._async_connection.close()
    
    async def on_cleanup(self):
        pass

class TestSteamRecentAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass
    
    async def asyncSetUp(self):
        self._async_connection:aiohttp.ClientSession = aiohttp.ClientSession()

    async def test_get_data(self):
        '''Function retrieves game data from the API'''
        response = await self._async_connection.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API}&steamid=76561198119238820")
                
        self.assertEqual(response.status, 200)
        response.close()
        self.addAsyncCleanup(self.on_cleanup)
    
    def tearDown(self):
        pass
    
    async def asyncTearDown(self):
        await self._async_connection.close()
    
    async def on_cleanup(self):
        pass

if __name__ == '__main__':
    unittest.main()