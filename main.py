import os
from pathlib import Path
import sys

from src.config.gdrive_config import GdriveConfig
from src.config.notion_config import NotionConfig
from src.downloader.service import DownloaderService
from src.gdrive.service import GdriveService
from src.markdown.image_substitution_feeder import ImageSubstitutionLineFeeder
from src.markdown.service import MarkdownService
from src.notion.repository import NotionRepository
from src.notion.service import NotionService


def main():
    if len(sys.argv) != 2:
        raise ValueError("Expecting a URL as a single argument")

    notion_url = sys.argv[1]

    notion_config = NotionConfig(env=os.environ)

    notion_repo = NotionRepository()
    notion_service = NotionService(
        notion_cookie_token=notion_config.token_v2, notion_repo=notion_repo
    )
    download_service = DownloaderService()
    markdown_service = MarkdownService()

    exported = notion_service.get_exported_url(notion_url)
    article_title = notion_service.get_article_title(notion_url)

    gdrive_config = GdriveConfig(article_title)
    gdrive_service = GdriveService(gdrive_config)

    download_info = download_service.download_file(exported, download_path="./tmp")

    image_mapping = {}
    for image in download_info.images:
        relative_path_image = Path.joinpath(download_info.base_path, image)
        image_url = gdrive_service.upload_img(image.name, str(relative_path_image))
        image_mapping[str(image)] = image_url

    markdown_service.add_line_feeder(ImageSubstitutionLineFeeder(image_mapping))

    for markdown in download_info.markdwons:
        markdown_service.process_file(
            Path.joinpath(download_info.base_path, markdown), markdown
        )


if __name__ == "__main__":
    main()
