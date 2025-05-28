import json
import os
import requests


def load_pod_links(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def download_image(url, save_path):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def download_all_images(json_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pod_links = load_pod_links(json_path)
    total = len(pod_links)
    success, failed = 0, 0

    for idx, pod in enumerate(pod_links, 1):
        docket_no = pod.get("DocketNo")
        url = pod.get("PODLink")
        if not docket_no or not url:
            continue

        ext = os.path.splitext(url)[-1] or ".png"
        filename = f"{docket_no}{ext}"
        save_path = os.path.join(output_folder, filename)

        print(f"🔄 Downloading {idx}/{total}: {filename}...")

        if download_image(url, save_path):
            success += 1
        else:
            failed += 1

    print(f"\n Downloaded: {success},  Failed: {failed}")


if __name__ == "__main__":
    download_all_images(
        json_path="../data/PODLinks.json",
        output_folder="data/raw"
    )
