#!/bin/bash
set -e

REPOS_DIRECTORY=/etc/ostree/remotes.d
URLS_WITH_PROBLEMS=()

get_update_platform_urls() {
    mapfile -t UPDATE_PLATFORM_URLS < <(grep -P -ho 'http[s]?.*' "${REPOS_DIRECTORY}"/*)
    if [[ ${#UPDATE_PLATFORM_URLS[@]} -eq 0 ]]; then
        echo "No update platforms found, this can be a mistake"
        exit 1
    fi
}

assert_update_platforms_are_responding() {
    for UPDATE_PLATFORM_URL in "${UPDATE_PLATFORM_URLS[@]}"; do
        HTTP_STATUS=$(curl -o /dev/null -Isw '%{http_code}\n' "$UPDATE_PLATFORM_URL" || echo "Unreachable")
        if ! [[ $HTTP_STATUS == 2* ]] && ! [[ $HTTP_STATUS == 3* ]]; then
            URLS_WITH_PROBLEMS+=( "$UPDATE_PLATFORM_URL" )
        fi
    done
    if [[ ${#URLS_WITH_PROBLEMS[@]} -eq 0 ]]; then
        echo "We can connect to all update platforms"
        exit 0
    else
        echo "There are problems connecting with the following URLs:"
        echo "${URLS_WITH_PROBLEMS[*]}"
        exit 1
    fi
}

if [[ ! -d $REPOS_DIRECTORY ]]; then
    echo "${REPOS_DIRECTORY} doesn't exist"
    exit 1
fi

get_update_platform_urls
assert_update_platforms_are_responding
