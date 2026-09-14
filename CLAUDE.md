# Movie Ratings

Flask + gunicorn + Postgres under Docker Compose. Deployed from this working
tree, so edits here go live on rebuild.

## Where things are

- Host `denmark` / 192.168.2.16, reachable as `ssh strombot@192.168.2.16`
- Source at `/root/movie-ratings` — root-owned, so reads and writes need `sudo`.
  `strombot` has passwordless sudo. `cd /root/...` as strombot fails; use
  `sudo bash -c "cd /root/movie-ratings && ..."`.
- Containers `movieratings_web` and `movieratings_db`
- Templates in `app/templates/`, static assets in `app/static/`
- Pushes to `git@github.com:clintons/Movie-Ratings.git`, branch `master`

## Read this before you debug the network

- **Port 5000 refuses connections from the LAN. That is correct.** It is bound
  to `127.0.0.1` so only the authentik outpost can reach it. The app trusts the
  `X-authentik-username` header, which is safe *only* while nothing else on the
  network can set it. Do not republish the port.
- **Port 3000 on this host is Grafana**, not this app. Port 80 is a stock nginx
  welcome page. Neither is related.
- **https://movie-ratings.tail648914.ts.net/ sits behind authentik SSO.** You
  cannot load a page there. Do not try to authenticate, and do not go looking
  for credentials.

## So how do you verify a change?

Not by fetching a page. Render the template in-container with a mock context:

    docker exec movieratings_web python3 -c "
    import sys; sys.path.insert(0,'/app')
    from app import app
    from flask import render_template
    with app.test_request_context('/'):
        print(render_template('index.html', movies=[...], page=1, total_pages=1,
              sort_by='title', order='ASC', search='', total=0, categories=[],
              genres=[], filter_category=None, filter_genre=None))"

Jinja errors only surface at render time, so this is the real test. Build rows
that hit every branch you touched.

Inspect data directly:

    docker exec movieratings_db psql -U postgres -d movieratings -c "SELECT ..."

## Deploying

Only `./data` and `./posters` are bind-mounted. **Template and static changes
need a rebuild** — editing a file on disk does nothing to the running app:

    sudo bash -c "cd /root/movie-ratings && docker compose build web && docker compose up -d web"

## Data gotchas

- `dad_rating`, `k_rating`, `spencer_rating` are `varchar(50)`, not integers.
  Coerce defensively and fall back to raw text.
- `dad_category` is free text with ~14 values (`Watchable`, `Good`, `Superb`,
  `Dud`, `DNF`, `PBS Mystery!`, ...). Match case-insensitively.
- Many rows have a category but no rating, or neither.
- Dad's rating renders as a cartoon pose, not a number (`dad_badge` macro in
  `app/templates/index.html`); K's and Spencer's stay numeric.

## Working tree

Uncommitted changes here are usually **already deployed** to the running
container, not work in progress. Check before assuming, and do not revert them:

    docker exec movieratings_web cat /app/app.py | diff - <(sudo cat /root/movie-ratings/app/app.py)

`master` is committed to directly; the history includes `Auto-sync from prod`
commits.
