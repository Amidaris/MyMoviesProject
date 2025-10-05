# uruchamianie konkretnych testów w cmd: pytest -v tests/test_tmdb.py lub wszystkich: pytest -v

import pytest
import tmdb_client
from tmdb_client import get_single_movie, get_movie_images, get_movie_cast, call_tmdb_api, get_movies_list
from unittest.mock import Mock
from main import app

def test_get_poster_url_uses_default_size():
   # Przygotowanie danych
   poster_api_path = "some-poster-path"
   expected_default_size = 'w342'
   # Wywołanie kodu, który testujemy
   poster_url = tmdb_client.get_poster_url(poster_api_path=poster_api_path)
   # Porównanie wyników
   assert expected_default_size in poster_url


def test_get_movies_list_type_popular():
   movies_list = tmdb_client.get_movies_list(list_type="popular")
   assert movies_list is not None


def test_get_movies_list(monkeypatch):
   # Lista, którą będzie zwracać przysłonięte "zapytanie do API"
   mock_movies_list = ['Movie 1', 'Movie 2']

   # Twprzenie obiektu Mock() 
   requests_mock = Mock()
   # Wynik wywołania zapytania do API
   response = requests_mock.return_value
   # Przysłaniamy wynik wywołania metody .json()
   response.json.return_value = mock_movies_list
   monkeypatch.setattr("tmdb_client.requests.get", requests_mock)

   movies_list = tmdb_client.get_movies_list(list_type="popular")
   assert movies_list == mock_movies_list
   

def test_get_single_movie(monkeypatch):
    mock_movie_id = "123"
    mock_movie_data = {
        "id": 123,
        "title": "Mocked Movie",
        "overview": "This is a mocked movie overview."
    }

    # Tworzymy mock dla requests.get
    requests_mock = Mock()
    response = requests_mock.return_value
    response.json.return_value = mock_movie_data
    response.raise_for_status = lambda: None

    # Podmieniamy requests.get w module tmdb_client
    monkeypatch.setattr("tmdb_client.requests.get", requests_mock)

    # Wywołujemy funkcję i sprawdzamy wynik
    result = get_single_movie(mock_movie_id)
    assert result == mock_movie_data


def test_get_movie_images(monkeypatch):
    mock_movie_id = "456"
    mock_images_data = {
        "backdrops": [{"file_path": "/image1.jpg"}],
        "posters": [{"file_path": "/poster1.jpg"}]
    }

    # Tworzymy mock dla requests.get
    requests_mock = Mock()
    response = requests_mock.return_value
    response.json.return_value = mock_images_data
    response.raise_for_status = lambda: None

    # Podmieniamy requests.get w module tmdb_client
    monkeypatch.setattr("tmdb_client.requests.get", requests_mock)

    # Wywołujemy funkcję i sprawdzamy wynik
    result = get_movie_images(mock_movie_id)
    assert result == mock_images_data


def test_get_movie_cast(monkeypatch):
    mock_movie_id = "789"
    mock_cast_data = [
        {"name": "Actor One", "character": "Hero"},
        {"name": "Actor Two", "character": "Villain"}
    ]

    # Tworzymy mock dla requests.get
    requests_mock = Mock()
    response = requests_mock.return_value
    response.json.return_value = {"cast": mock_cast_data}
    response.raise_for_status = lambda: None

    # Podmieniamy requests.get w module tmdb_client
    monkeypatch.setattr("tmdb_client.requests.get", requests_mock)

    # Wywołujemy funkcję i sprawdzamy wynik
    result = get_movie_cast(mock_movie_id)
    assert result == mock_cast_data


def test_call_tmdb_api(monkeypatch):
    mock_data = {"key": "value"}
    requests_mock = Mock()
    response = requests_mock.return_value
    response.json.return_value = mock_data
    response.raise_for_status = lambda: None

    monkeypatch.setattr("tmdb_client.requests.get", requests_mock)

    result = call_tmdb_api("movie/popular")
    assert result == mock_data


def test_homepage(monkeypatch):
   api_mock = Mock(return_value={'results': []})
   monkeypatch.setattr("tmdb_client.call_tmdb_api", api_mock)

   with app.test_client() as client:
       response = client.get('/')
       assert response.status_code == 200
       api_mock.assert_called_once_with('movie/popular')


@pytest.mark.parametrize("list_type", [
    "popular",
    "top_rated",
    "upcoming",
    "now_playing"
])

def test_get_movies_list_with_valid_types(monkeypatch, list_type):
    mock_data = {"results": [f"Mocked movie for {list_type}"]}
    
    def mock_call_tmdb_api(endpoint):
        assert endpoint == f"movie/{list_type}"
        return mock_data

    monkeypatch.setattr("tmdb_client.call_tmdb_api", mock_call_tmdb_api)

    result = get_movies_list(list_type)
    assert result == mock_data