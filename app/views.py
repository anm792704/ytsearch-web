import flask
import httplib2
from googleapiclient import discovery
from flask import render_template, request
from oauth2client import client

from app import app
from app.YtVideo import YtVideo
from app.search_form import SearchForm

result = {}
resultList = []

@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:

        #channel = youtube.channels().list(mine=True, part='snippet').execute()
        #return json.dumps(channel)

        return flask.redirect(flask.url_for('search_form'))

        playlists_list_by_channel_id(youtube,
            part='snippet,contentDetails',
            channelId='UCZ0DJ1UBmS1sEjDBr2OABAw',
            maxResults=50)

        return render_template('result.html', title='Videos', resultList=resultList)


@app.route('/search_form', methods=['GET', 'POST'])
def search_form():
    searchForm = SearchForm()
     resultList.clear()

    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))

    http_auth = credentials.authorize(httplib2.Http())
    youtube = discovery.build('youtube', 'v3', http_auth)

    if request.method == 'POST':
        # title = searchForm.title.data
        #description1 = searchForm.description1.data
        #description2 = searchForm.description2.data

        playlists_list_by_channel_id(youtube,
                                     searchForm.title.data,
                                     searchForm.description1.data,
                                     searchForm.description2.data,
                                     part='snippet,contentDetails',
                                     channelId='UCZ0DJ1UBmS1sEjDBr2OABAw',
                                     maxResults=50)

        return render_template('result.html', title='Videos', resultList=resultList)
    elif request.method == 'GET':
        return render_template('search_form.html', searchForm = searchForm)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secret.json',
    scope='https://www.googleapis.com/auth/youtube.force-ssl',
    redirect_uri=flask.url_for('oauth2callback', _external=True))

    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))


def playlists_list_by_channel_id(service,
                                 title,
                                 description1,
                                 description2,
                                 **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)  # See full sample for function
    results = service.playlists().list(
        **kwargs
    ).execute()

    #return print_results(results)

    playlist_idx = 0
    while playlist_idx < len(results['items']):
        playlist_items_list_by_playlist_id(service,
                                           title=title,
                                           description1=description1,
                                           description2=description2,
                                           part='snippet, contentDetails',
                                           maxResults=25,
                                           playlistId=results['items'][playlist_idx]['id'])

        playlist_idx = playlist_idx + 1

def playlist_items_list_by_playlist_id(service,
                                       title,
                                       description1,
                                       description2,
                                       **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)  # See full sample for function
    results = service.playlistItems().list(
        **kwargs
    ).execute()

    #print_results(results)

    playlist_item_idx = 0
    while playlist_item_idx < len(results['items']):
        video_title_lower = results['items'][playlist_item_idx]['snippet']['title'].lower()
        video_description_lower = results['items'][playlist_item_idx]['snippet']['description'].lower()

        title = title
        description1 = description1
        description2 = description2

        if title is not None:
            search_title_lower = title.lower()
            if (search_title_lower in video_title_lower):
                if description1 is not None:
                    search_description1_lower = description1.lower()
                    if (search_description1_lower in video_description_lower):
                        if description2 is not None:
                            search_description2_lower = description2.lower()
                            if (search_description2_lower in video_description_lower):
                                print_results(results, playlist_item_idx)
                        else:
                            print_results(results, playlist_item_idx)
                else:
                    print_results(results, playlist_item_idx)
        else:
            if description1 is not None:
                search_description1_lower = description1.lower()
                if (search_description1_lower in video_description_lower):
                    if description2 is not None:
                        search_description2_lower = description2.lower()
                        if (search_description2_lower in video_description_lower):
                            print_results(results, playlist_item_idx)
                    else:
                        print_results(results, playlist_item_idx)
        playlist_item_idx = playlist_item_idx + 1

def print_results(results, playlist_item_idx):
     #"Title: " + results['items'][playlist_item_idx]['snippet']['title']
    result.update({'title' : results['items'][playlist_item_idx]['snippet']['title'],
                  'description' : results['items'][playlist_item_idx]['snippet']['description'],
                   'url' : results['items'][playlist_item_idx]['snippet']['resourceId']['videoId']})
    ytvideo = YtVideo(results['items'][playlist_item_idx]['snippet']['title'],
                      results['items'][playlist_item_idx]['snippet']['description'],
                      results['items'][playlist_item_idx]['snippet']['resourceId']['videoId'])
    ytvideo2 = dict(title=results['items'][playlist_item_idx]['snippet']['title'],
                      description=results['items'][playlist_item_idx]['snippet']['description'],
                      url=results['items'][playlist_item_idx]['snippet']['resourceId']['videoId'])

    #resultList.append(ytvideo)
    resultList.append(ytvideo2)




def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
            # Convert a name like "snippet.tags[]" to snippet.tags, but handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True
            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource
