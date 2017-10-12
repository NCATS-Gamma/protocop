from greent.chemotext import Chemotext
from greent.oxo import OXO
import json
import logging
from graph_components import KEdge

#TODO: where is code like this going to go?  Is it up to OXO? greent? something higher?  Built into the nodes?
def OXOdise_term(term):
    """Convert IRIs into CURIEs.
    
    Sometimes biolink or other sources will give an id like: http://purl.obolibrary.org/obo/OMIM_603903. 
    OXO expects: OMIM:603903.
    At least for the ones we've seen so far, the format has been that the last element in the url is
    the curie, but with : replaced by _."""
    if not term.startswith('http'):
        return term
    iri_term = term.split('/')[-1]
    if iri_term.count('_') != 1:
        logging.getLogger('application').warn('Invalid term for OXO: %s' % term)
        return term
    return ':'.join(iri_term.split('_'))

def convert_to_mesh(term):
    """Use OXO to convert an id(doid, etc) to MeSH"""
    #Check to see if we already have a MeSH curie
    if term[:5].upper() == 'MESH':
        return [term]
    #sometimes terms are not good for OXO, like http://purl.obolibrary.org/obo/OMIM_603903. OXO expects OMIM:603903
    term = OXOdise_term(term)
    oxo = OXO()
    response = oxo.query([ term ])
    #ugly, and probably wrong
    search_results = response['_embedded']['searchResults'][0]['mappingResponseList']
    meshes = []
    for result in search_results:
        if result['targetPrefix'] == 'MeSH':
            meshes.append( result )
    if len(meshes) == 0:
        logging.getLogger('application').warn('No MeSH ID found for term: %s' % term)
    return meshes

def get_mesh_terms(node):
    MESH_KEY = 'mesh_identifiers'
    if MESH_KEY not in node.properties:
        node.properties[MESH_KEY] =  convert_to_mesh( node.identifier ) 
    return node.properties[MESH_KEY]

def term_to_term(node_a,node_b, limit = 10):
    """Given two terms, find articles in chemotext that connect them, and return as a KEdge.
    If nothing is found, return None"""
    meshes_a = get_mesh_terms(node_a)
    meshes_b = get_mesh_terms(node_b)
    ctext = Chemotext( )
    articles=[]
    for ma in meshes_a:
        label_a = ma['label']
        for mb in meshes_b:
            label_b = mb['label']
            response = ctext.query( query="MATCH (d:Term)-[r1]-(a:Art)-[r2]-(t:Term) WHERE d.name='%s' AND t.name='%s' RETURN a LIMIT %d" % (label_a, label_b, limit))
            for result in response['results']:
                for data in result['data']:
                    articles += data['row']
    if len(articles) > 0:
        return KEdge( 'chemotext', 'support', { 'publications': articles } )
    return None

if __name__ == '__main__':
    print( term_to_term('DOID:4325', 'DOID:14504') )
    #print term_to_term('DOID:4325', 'http://www.orpha.net/ORDO/Orphanet_646')
