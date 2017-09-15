import sys
import io
import requests
import lob

GOOGLE_API_KEY = 'AIzaSyDhp25baf-y_KqgQxRb-Pigp3NP2XdTlpQ'
lob.api_key = 'test_176ba059dc3becbc0602eb3bac42e545a26'

def parse_file(input_file):
    data = {}
    with io.open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            key, val = line.replace(u'\u2019', u'\'').split(':')
            data[key.lower()] = val
    return data

def get_from_address(data):
    return {
        'name': data['from name'],
        'address_line1': data['from address line 1'],
        'address_line2': data['from address line 2'],
        'address_city': data['from city'],
        'address_state': data['from state'],
        'address_zip': data['from zip code'],
    }

def get_address_string(address):
    address_string = ''
    for key in ['address_line1','address_line2', 'address_city','address_state','address_zip']:
        address_string += address[key]
    return address_string

def get_to_address(from_address):
    from_address_string = get_address_string(from_address)
    response = requests.get(('https://www.googleapis.com/civicinfo/v2/representatives?'
                             'key={0}&'
                             'address={1}&'
                             'roles=headOfGovernment&'
                             'levels=administrativeArea1').format(GOOGLE_API_KEY,from_address_string)
                            )
    official = response.json()['officials'][0]
    official_addr = official['address'][0]
    return {
        'name': official['name'],
        'address_line1': official_addr['line1'],
        'address_line2': official_addr['line2'],
        'address_city': official_addr['city'],
        'address_state': official_addr['state'],
        'address_zip': official_addr['zip'],
    }

def create_letter():
    data = parse_file(sys.argv[1])
    try:
        from_address = get_from_address(data)
    except:
        print ('Your input doesn\'t match, check sample_input.txt for reference')

    try:
        to_address = get_to_address(from_address)
    except:
        print ('I couldn\'t find a the head of government in your area')

    letter = lob.Letter.create(
          description = 'Demo Letter',
          to_address = to_address,
          from_address = from_address,
          file = '<html style="padding-top: 3in; margin: .5in;">{{message}}</html>',
          merge_variables = {
            'message': data['message']
          },
          color = True
    )
    print(letter['url'])

def main():
    #check arguments
    if len(sys.argv) != 2:
        "usage: python send_legisator_letter.py <input_file.txt>"

    create_letter()

if __name__ == '__main__':
  main()