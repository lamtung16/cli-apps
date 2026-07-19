import requests

def filter(MODE, BASE_URL, USERNAME, PASSWORD, field, value):
    params = {
        "username": USERNAME,
        "password": PASSWORD,
        "action": "get_live_streams" if MODE == 1 else "get_vod_streams"
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"}
    response = requests.get(BASE_URL + "/player_api.php", params=params, headers=headers, timeout=10)
    response.raise_for_status()
    streams = response.json()
    output_streams = [s for s in streams if str(value).lower() in str(s.get(field).lower())]
    return output_streams

def main():
    base_url = "http://s.rocketdns.info:8080"
    username = "fenderfox"
    password = "112694"

    while True:
        print("0. Edit source")
        print("1. Live TV")
        print("2. VOD")
        print("3. Exit")
        mode = int(input("Your choice: "))
        if mode == 0:
            base_url = input("Base url: ")
            username = input("Username: ")
            password = input("Password: ")
        elif mode == 1:
            while True:
                key = input("key: ")
                for channel in filter(mode, base_url, username, password, "name", key):
                    stream_id = channel.get("stream_id")
                    channel_name = channel.get("name")
                    url = f"{base_url.rstrip('/')}/{username}/{password}/{stream_id}"
                    print(f"{channel_name}: {url}")
                
                exit = input("Exit (y/n): ")
                if exit == "y":
                    break
        elif mode == 2:
            while True:
                key = input("key: ")
                for channel in filter(mode, base_url, username, password, "name", key):
                    stream_id = channel.get("stream_id")
                    channel_name = channel.get("name")
                    url = f"{base_url.rstrip('/')}/movie/{username}/{password}/{stream_id}.mp4"
                    print(f"{channel_name}: {url}")
                
                exit = input("Exit (y/n): ")
                if exit == "y":
                    break
        else:
            print("Bye (^-^)")
            break

if __name__ == "__main__":
    main()