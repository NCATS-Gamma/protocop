import logging

def lookup_disease_by_name( disease_name, greent ):
    """We can have different parameterizations if necessary.
    Here, we first get a mondo ID.  Then we try to turn that into
    (in order), a DOID, a UMLS, and an EFO.
    Return type is a list of identifiers."""
    logger=logging.getLogger('application')
    #This performs a case-insensitive exact match, and also inverts comma-ed names
    mondo_ids =  greent.mondo.search( disease_name )
    if len(mondo_ids) == 0:
        logger.error('Could not convert disease name: {}. Exiting.'.format(disease_name))
        return []
    logging.getLogger('application').debug('Found mondo identifiers for {}'.format(disease_name))
    for mid in mondo_ids:
        logger.debug('  {}  {}'.format(mid, greent.mondo.get_label(mid)))
    doids = sum([ greent.mondo.mondo_get_doid( r ) for r in mondo_ids], [] )
    if len(doids) > 0:
        logger.debug('Returning: {}'.format(' '.join(doids)))
        return doids
    umls = sum([ greent.mondo.mondo_get_umls( r ) for r in mondo_ids], [] )
    if len(umls) > 0:
        logger.debug('Returning: {}'.format(' '.join(umls)))
        return umls
    efos = sum([ greent.mondo.mondo_get_efo( r ) for r in mondo_ids], [] )
    if len(efos) > 0:
        logger.debug('Returning: {}'.format(' '.join(efos)))
        return efos
    logger.error('For disease name: "{}" found mondo ID(s): {}, but could not transform to another identifier system. Exiting.'.format(disease_name, ';'.join(mondo_ids)))
    return []
    

def lookup_drug_by_name( drug_name, greent ):
    """Look up drugs by name.  We will pull results from multiple sources in this case,
    and return them all."""
    logger=logging.getLogger('application')
    logger.debug('Looking up drug name: {}'.format(drug_name) )
    #CTD
    ctd_ids = greent.ctd.drugname_string_to_ctd_string( drug_name )
    #PHAROS
    pids_and_labels = greent.pharos.drugname_string_to_pharos_info( drug_name )
    pharos_ids = [x[0] for x in pids_and_labels]
    #PUBCHEM
    pubchem_info = greent.chembio.drugname_to_pubchem( drug_name )
    pubchem_ids = [ 'PUBCHEM:{}'.format(r['drugID'].split('/')[-1]) for r in pubchem_info ]
    #TOTAL:
    drug_ids = ctd_ids + pharos_ids + pubchem_ids
    logger.debug( drug_ids )
    return drug_ids


def test():
    from greent.rosetta import Rosetta
    r = Rosetta()
    names = ['BUTYLSCOPOLAMINE','ADAPALENE','NADIFLOXACIN','TAZAROTENE']
    for name in names:
        print ( name, lookup_drug_by_name( name , r.core) )

if __name__ == '__main__':
    test()
