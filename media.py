from urllib.parse import urlparse, parse_qs
import requests


def parse_source(text):
    """
    Accepts:

        host username password
        host,username,password

        http://host:8080/get.php?username=user&password=pass
        http://host:8080/player_api.php?username=user&password=pass

    Returns:
        base_url, username, password
    """

    text = text.strip()

    # ---------------------------------------------------------
    # Format: URL?username=xxx&password=xxx
    # ---------------------------------------------------------
    if "?" in text:
        parsed = urlparse(text)

        query = parse_qs(parsed.query)

        username = query.get("username", [None])[0]
        password = query.get("password", [None])[0]

        if not username or not password:
            raise ValueError(
                "URL must contain username and password."
            )

        # Keep scheme + host + port, remove /get.php etc.
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL.")

        return base_url.rstrip("/"), username, password

    # ---------------------------------------------------------
    # Format: host,username,password
    # ---------------------------------------------------------
    if "," in text:
        parts = [x.strip() for x in text.split(",")]

        if len(parts) != 3:
            raise ValueError(
                "Expected: host,username,password"
            )

        base_url, username, password = parts

        if not base_url.startswith(("http://", "https://")):
            base_url = "http://" + base_url

        return base_url.rstrip("/"), username, password

    # ---------------------------------------------------------
    # Format: host username password
    # ---------------------------------------------------------
    parts = text.split()

    if len(parts) == 3:
        base_url, username, password = parts

        if not base_url.startswith(("http://", "https://")):
            base_url = "http://" + base_url

        return base_url.rstrip("/"), username, password

    raise ValueError(
        "Could not understand the source format."
    )


def edit_source(base_url, username, password):
    print("\n=== Edit Source ===")
    print("1. Manual")
    print("2. Automatic")
    print("0. Back")

    try:
        choice = int(input("Choose option: "))
    except ValueError:
        print("Invalid choice.")
        return base_url, username, password

    # ---------------------------------------------------------
    # Manual
    # ---------------------------------------------------------
    if choice == 1:
        base_url = input("Base url: ").strip()
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        return base_url.rstrip("/"), username, password

    # ---------------------------------------------------------
    # Automatic
    # ---------------------------------------------------------
    elif choice == 2:
        source = input("\nPaste source: ").strip()

        try:
            base_url, username, password = parse_source(source)

            print("\nSource detected successfully.")
            print(f"Host: {base_url}")
            print(f"Username: {username}")
            print("Password: ********")

            return base_url, username, password

        except ValueError as e:
            print(f"\nInvalid source: {e}")
            return base_url, username, password

    elif choice == 0:
        return base_url, username, password

    else:
        print("Invalid choice.")
        return base_url, username, password


def api_request(BASE_URL, USERNAME, PASSWORD, action):
    params = {
        "username": USERNAME,
        "password": PASSWORD,
        "action": action
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        BASE_URL.rstrip("/") + "/player_api.php",
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    return response.json()


def list_live_tv(BASE_URL, USERNAME, PASSWORD):
    categories = api_request(
        BASE_URL,
        USERNAME,
        PASSWORD,
        "get_live_categories"
    )

    if not categories:
        print("No Live TV categories found.")
        return

    streams = api_request(
        BASE_URL,
        USERNAME,
        PASSWORD,
        "get_live_streams"
    )

    while True:
        print("\n=== Live TV Categories ===")

        for i, category in enumerate(categories, start=1):
            print(
                f"{i}. "
                f"{category.get('category_name', 'Unknown')}"
            )

        print("0. Back")

        try:
            choice = int(input("\nChoose category: "))
        except ValueError:
            print("Invalid choice.")
            continue

        if choice == 0:
            break

        if choice < 1 or choice > len(categories):
            print("Invalid choice.")
            continue

        selected_category = categories[choice - 1]

        category_id = str(
            selected_category.get("category_id")
        )

        category_name = selected_category.get(
            "category_name",
            "Unknown"
        )

        channels = [
            stream
            for stream in streams
            if str(stream.get("category_id")) == category_id
        ]

        print(f"\n=== {category_name} ===")

        if not channels:
            print("No channels found in this category.")
            continue

        for i, channel in enumerate(channels, start=1):
            stream_id = channel.get("stream_id")
            channel_name = channel.get("name", "Unknown")

            url = (
                f"{BASE_URL.rstrip('/')}/live/"
                f"{USERNAME}/{PASSWORD}/"
                f"{stream_id}.m3u8"
            )

            print(f"{i}. {channel_name}")
            print(f"   {url}")


def search_movies(BASE_URL, USERNAME, PASSWORD):
    print("\nLoading movies...")

    movies = api_request(
        BASE_URL,
        USERNAME,
        PASSWORD,
        "get_vod_streams"
    )

    if not movies:
        print("No movies found.")
        return

    while True:
        key = input(
            "\nSearch movie (or 0 to go back): "
        ).strip()

        if key == "0":
            break

        if not key:
            print("Please enter a movie name.")
            continue

        results = [
            movie
            for movie in movies
            if key.lower() in str(
                movie.get("name", "")
            ).lower()
        ]

        print(f"\n=== Search results for: {key} ===")

        if not results:
            print("No movies found.")
            continue

        for i, movie in enumerate(results, start=1):
            stream_id = movie.get("stream_id")
            movie_name = movie.get("name", "Unknown")
            extension = movie.get(
                "container_extension",
                "mp4"
            )

            url = (
                f"{BASE_URL.rstrip('/')}/movie/"
                f"{USERNAME}/{PASSWORD}/"
                f"{stream_id}.{extension}"
            )

            print(f"{i}. {movie_name}")
            print(f"   {url}")


def main():
    base_url = "http://goldenpass.xyz:80"
    username = "4FC6429D06775D0"
    password = "nITKw2eFdI"

    while True:
        print("\n0. Edit source")
        print("1. Live TV")
        print("2. Search Movie")
        print("3. Exit")

        try:
            mode = int(input("Your choice: "))
        except ValueError:
            print("Invalid choice.")
            continue

        if mode == 0:
            base_url, username, password = edit_source(
                base_url,
                username,
                password
            )

        elif mode == 1:
            try:
                list_live_tv(
                    base_url,
                    username,
                    password
                )
            except requests.RequestException as e:
                print(f"Request failed: {e}")
            except ValueError:
                print("Invalid response from server.")

        elif mode == 2:
            try:
                search_movies(
                    base_url,
                    username,
                    password
                )
            except requests.RequestException as e:
                print(f"Request failed: {e}")
            except ValueError:
                print("Invalid response from server.")

        elif mode == 3:
            print("Bye (^-^)")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()