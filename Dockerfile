# Copyright (c) 2020 Vincent A. Cicirello
# https://www.cicirello.org/
# Licensed under the MIT License
FROM cicirello/pyaction-lite:latest
COPY JacocoBadgeGenerator.py /JacocoBadgeGenerator.py
ENTRYPOINT ["/JacocoBadgeGenerator.py"]
