#!/usr/bin/env python3.4
import ursgal
import pprint
import xml.etree.ElementTree
import os
import platform
import sys
import subprocess
import csv

if sys.platform != 'win32':
    csv.field_size_limit(sys.maxsize)

class omssa_2_1_9( ursgal.UNode ):
    """
    omssa_2_1_9 UNode

    Parameter options at http://www.ncbi.nlm.nih.gov/IEB/ToolBox/CPP_DOC/asn_spec/omssa.asn.html

    2.1.9 parameters at http://proteomicsresource.washington.edu/protocols06/omssa.php

    Reference:
    Geer LY, Markey SP, Kowalak JA, Wagner L, Xu M, Maynard DM, Yang X, Shi W, Bryant SH (2004) Open Mass Spectrometry Search Algorithm.

    """
    META_INFO = {
        'engine_type'            : {
            'controller'        : False,
            'converter'         : False,
            'validation_engine' : False,
            'search_engine'     : True,
            'meta_engine'       : False
        },
        'citation'              : 'Geer LY, Markey SP, Kowalak JA, '\
            'Wagner L, Xu M, Maynard DM, Yang X, Shi W, Bryant SH (2004) '\
            'Open Mass Spectrometry Search Algorithm.',
        'input_types'           : ['.mgf'],
        'output_extension'      : '.csv',
        'create_own_folder'     : True,
        'in_development'        : False,

        'include_in_git'        : False,
        'utranslation_style'    : 'omssa_style_1',
        ### Below are the download information ###
        'engine': {
            'darwin' : {
                '64bit' : {
                    'exe'            : 'omssacl',
                    'url'            : 'ftp://ftp.ncbi.nih.gov/pub/lewisg/omssa/2.1.9/omssa-2.1.9.macos.tar.gz',
                    'zip_md5'        : '9cb92a98c4d96c34cc925b9336cbaec7',
                    'additional_exe' : ['makeblastdb'],
                },
            },
            'linux' : {
                '64bit' : {
                    'exe'            : 'omssacl',
                    'url'            : 'ftp://ftp.ncbi.nih.gov/pub/lewisg/omssa/2.1.9/omssa-2.1.9.linux.tar.gz',
                    'zip_md5'        : '921e01df9cd2a99d21e9a336b5b862c1',
                    'additional_exe' : ['makeblastdb'],
                },
            },
            'win32' : {
                '64bit' : {
                    'exe'            : 'omssacl.exe',
                    'url'            : 'ftp://ftp.ncbi.nih.gov/pub/lewisg/omssa/2.1.9/omssa-2.1.9.win32.exe',
                    'zip_md5'        : 'b9d9a8aec3cfe77c48ce0f5752aba8f9',
                    'additional_exe' : ['makeblastdb'],
                },
                '32bit' : {
                    'exe'            : 'omssacl.exe',
                    'url'            : 'ftp://ftp.ncbi.nih.gov/pub/lewisg/omssa/2.1.9/omssa-2.1.9.win32.exe',
                    'zip_md5'        : 'a05a5cdd45fd8abcfc75b1236f8a2390',
                    'additional_exe' : ['makeblastdb'],
                },
            },
        },
        'mods_to_unimod_correction' : {
            # this dict holds corrections of wrong OMSSA to unimod assignments
            'TMT 6-plex on K' : {
                'unimod_id'       : '737',
                'ommsa_unimod_id' : '738', # this is TMT duplex in unimod
                'unimod_name'     : 'TMT6plex',
            },
            'TMT 6-plex on n-term peptide' : {
                'unimod_id'       : '737',
                'ommsa_unimod_id' : '738', # this is TMT duplex in unimod
                'unimod_name'     : 'TMT6plex',
                'aa_targets'      : ['N-term'] # override 'X' in OMSSA mods xml
            },
            'TMT duplex on K': {
                'unimod_id'       : '738',
                'ommsa_unimod_id' : '738', # this is TMT duplex in unimod
                'unimod_name'     : 'TMT2plex'
            },
            'TMT duplex on n-term peptide': {
                'unimod_id'       : '738',
                'ommsa_unimod_id' : '738', # this is TMT duplex in unimod
                'unimod_name'     : 'TMT2plex',
                'aa_targets'      : ['N-term'] # override 'X' in OMSSA mods xml
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(omssa_2_1_9, self).__init__(*args, **kwargs)
        self.omssa_mod_Mapper = None

    def _load_omssa_xml(self):
        ''' Parsing through omssa mods to map omssa mods on unimods '''
        self.omssa_mod_Mapper = {}
        def _create_empty_tmp():
            tmp = {
                'aa_targets' : [],
            }
            return tmp
        tmp = _create_empty_tmp()
        xml_path = os.path.dirname( self.exe )

        xml_names = ['mods.xml', 'usermods.xml']
        for xml_name in xml_names:
            omssa_xml = os.path.join(
                xml_path,
                xml_name
            )
            self.print_info(
                'Parsing omssa xml ({0})'.format(
                     omssa_xml
                ),
                caller='__ini__'
            )
            for event, element in xml.etree.ElementTree.iterparse( omssa_xml ):
                if element.tag.endswith('MSModSpec_residues_E'):
                    tmp['aa_targets'].append( element.text )

                elif element.tag.endswith('MSMod'):
                    tmp['omssa_id'] = element.text
                    # tmp['MSMod'] = element.text # OMSSA ID!
                elif element.tag.endswith('MSModSpec_psi-ms'):
                    tmp['unimod_name'] = element.text
                elif element.tag.endswith('MSModSpec_unimod'):
                    tmp['unimod_id'] = element.text
                    # tmp['MSModSpec_psi-ms'] = element.text # UNIMOD Name
                elif element.tag.endswith('MSModSpec_name'):
                    tmp['omssa_name'] = element.text
                    additional = []
                    if 'protein' in tmp['omssa_name']:
                        additional.append( 'Prot' )
                    if 'n-term' in tmp['omssa_name']:
                        additional.append('N-term')
                    elif 'c-term' in  tmp['omssa_name']:
                        additional.append('C-term')
                    if len(additional) > 0:
                        tmp['aa_targets'].append( '-'.join( additional ))

                elif element.tag.endswith('MSModSpec'):
                    lookup_field = 'unimod_id'
                    try:
                        l_value = tmp[ lookup_field ]
                    except:
                        self.print_info(
                            'Skipping entry {0} (no unimod! map)'.format( tmp ),
                            caller='WARNING!'
                        )
                        tmp['aa_targets'] = []
                        continue
                    if tmp['omssa_name'] in self.META_INFO['mods_to_unimod_correction'].keys():
                        l_value = self.META_INFO['mods_to_unimod_correction'][tmp['omssa_name']]['unimod_id']
                        # for TMT mods OMSSA writes an 'X' as amino acid target, this breaks later code...
                        if 'aa_targets' in self.META_INFO['mods_to_unimod_correction'][tmp['omssa_name']].keys():
                            tmp['aa_targets'] = self.META_INFO['mods_to_unimod_correction'][tmp['omssa_name']]['aa_targets']
                    if l_value not in \
                            self.omssa_mod_Mapper.keys():
                        self.omssa_mod_Mapper[ l_value ] = {}
                    self.omssa_mod_Mapper[ l_value ][ tmp[ 'omssa_id' ] ] = {
                        'aa_targets' : tmp[ 'aa_targets' ],
                        'omssa_name' : tmp[ 'omssa_name' ]
                    }

                    tmp = _create_empty_tmp()
        return

    def preflight( self ):
        '''
        Formatting the command line via self.params

        unimod Modifications are translated to OMSSA modifications

        Returns:
                self.params(dict)
        '''
        if self.omssa_mod_Mapper is None:
            self._load_omssa_xml()

        # building command_list !
        translations = self.params['translations']['_grouped_by_translated_key']

        blastdb_suffixes = [ '.phr', '.pin', '.psq' ]
        blastdb_present = True
        for blastdb_suffix in blastdb_suffixes:
            blast_file = self.params['database'] + blastdb_suffix
            if os.path.exists( blast_file ) is False:
                blastdb_present = False
                break

        if blastdb_present is False:
            self.print_info('Executing makeblastdb...')
            proc = subprocess.Popen(
                [
                    os.path.join(
                        os.path.dirname( self.exe ),
                        'makeblastdb'
                    ),
                    '-in', self.params['translations']['database'],
                    '-dbtype', 'prot',
                    '-input_type', 'fasta',
                ],
                stdout=subprocess.PIPE,
            )
            for line in proc.stdout:
                print(line.strip().decode('utf'))

        if self.params['translations']['label'] == '15N':
            translations['-tem']['precursor_mass_type'] = '2'
            translations['-tom']['frag_mass_type'] = '2'

        # Modifications
        # ------------------------

        for param_key in ['_fixed_mods', '_opt_mods']:
            mod_type = param_key[1:4]
            modifications = ''
            self.params[ param_key ] = ''
            for mod in self.params[ 'mods' ][ mod_type ]:
                unimod_id_does_not_exist = False
                aa_can_not_be_mapped = True
                # print(mod['id'])
                # print(self.omssa_mod_Mapper.keys())
                if mod[ 'id' ] not in self.omssa_mod_Mapper.keys():
                    unimod_id_does_not_exist = True
                else:
                    if mod['aa'] == '*':
                        search_target = [ mod[ 'pos' ], ]
                    else:
                        search_target = [ mod['aa'], ]
                    for omssa_id in self.omssa_mod_Mapper[ mod[ 'id' ] ].keys():
                        if search_target == self.omssa_mod_Mapper[ mod[ 'id' ] ][ omssa_id ]['aa_targets']:
                            modifications += '{0},'.format( omssa_id )
                            aa_can_not_be_mapped = False
                            omssa_name = self.omssa_mod_Mapper[ mod[ 'id' ] ][ omssa_id ]['omssa_name']
                            self.lookups[ omssa_name ] = {
                                'name'       : mod[ 'name' ],
                                'aa_targets' : self.omssa_mod_Mapper[ mod[ 'id' ] ][ omssa_id ]['aa_targets'],
                                'omssa_id'   : omssa_id,
                                'id'         : mod['id']
                            }
                # print(unimod_id_does_not_exist)
                # print(aa_can_not_be_mapped)
                if unimod_id_does_not_exist or aa_can_not_be_mapped:
                    self.print_info( '''
    The combination of modification name and aminoacid is not supported by
    OMSSA. Continuing without modification: {0}
                    '''.format(mod),
                    caller='WARNING'
                    )
                    continue

            self.params[ param_key ] = modifications.strip(',')

        # exit(1)
        # semi-enyzmatic cleavage --> translation into omssa enzyme number
        if self.params['translations']['semi_enzyme'] is True:
            if translations['-e']['enzyme'] == '0':
                translations['-e']['enzyme'] = '16'
            elif translations['-e']['enzyme'] == '3':
                translations['-e']['enzyme'] = '23'
            elif translations['-e']['enzyme'] == '13':
                translations['-e']['enzyme'] = '24'

        if self.params['translations']['frag_mass_tolerance_unit'] == 'ppm':
            translations['-to']['frag_mass_tolerance'] = \
                ursgal.ucore.convert_ppm_to_dalton(
                    self.params['translations']['frag_mass_tolerance'],
                    base_mz=self.params['translations']['base_mz']
                )

        self.params['_omssa_precursor_error'] = (
            float(self.params['translations']['precursor_mass_tolerance_plus']) + \
            float(self.params['translations']['precursor_mass_tolerance_minus']) \
        ) / 2.0

        self.params['_tmp_output_file_incl_path'] = os.path.join(
            self.params['output_dir_path'],
            self.params['output_file'] + '_tmp'
        )
        self.created_tmp_files.append( self.params['_tmp_output_file_incl_path'] )

        self.params['translations']['output_file_incl_path'] = os.path.join(
            self.params['output_dir_path'],
            self.params['output_file']
        )
        self.params['translations']['mgf_input_file'] = os.path.join(
            self.params['input_dir_path'],
            self.params['input_file']
        )
        translations['-fm']['mgf_input_file'] = self.params['translations']['mgf_input_file']

        assert os.path.exists( self.params['translations']['mgf_input_file']  ), '''
        OMSSA requires .mgf input (which should have been generated
        automatically ...)
        '''

        self.params['command_list'] = [
            self.exe,  # path 2 omssa executable
            '-w',
        ]

        for translated_key, translation_dict in translations.items():
            translated_value = str(list(translation_dict.values())[0])
            if translated_key == ('-oc', '-ox'):
                self.params['command_list'].extend( (translated_value, self.params['_tmp_output_file_incl_path']) )
                continue
            elif translated_key == '-te':
                self.params['command_list'].extend( (translated_key, str(self.params['_omssa_precursor_error'])) )
                continue
            elif translated_key in ['-teppm', '-ni']:
                if translated_value != '':
                    self.params['command_list'].append(translated_value)
                else:
                    continue
            elif translated_key == ('-mv', 'mf'):
                if self.params['_opt_mods'] != '':
                    self.params['command_list'].extend( ('-mv', self.params['_opt_mods']) )
                if self.params['_fixed_mods'] != '':
                    self.params['command_list'].extend( ('-mf', self.params['_fixed_mods']) )
                continue
            elif translated_key == '-i':
                ions_2_add = []
                for k, v in translations['-i'].items():
                    if v != '':
                        ions_2_add.append(v)
                self.params['command_list'].extend( ('-i', ','.join(sorted(ions_2_add)) ) )
                continue
            elif translated_key in [
                ('-tem','-tom'),
                'label',
                'semi_enzyme',
                'base_mz',
                'header_translations',
                'frag_mass_tolerance_unit',
            ]:
                continue
            elif len(translation_dict) == 1:
                self.params['command_list'].extend( (translated_key, translated_value) )
            else:
                print('The translatd key ', translated_key, ' maps on more than one ukey, but no special rules have been defined')
                print(translation_dict)
                exit(1)

    def postflight( self ):
        '''
        Will correct the OMSSA headers and add the column retention time to the
        csv file
        '''
        cached_omssa_output = []
        result_file = open( self.params['_tmp_output_file_incl_path'], 'r')
        csv_dict_reader_object = csv.DictReader(
            row for row in result_file if not row.startswith('#')
        )
        headers = csv_dict_reader_object.fieldnames
        header_translations = self.UNODE_UPARAMS['header_translations']['uvalue_style_translation']
        translated_headers = []
        for header in headers:
            if header in [' E-value',' P-value']:
                continue
            translated_headers.append(
                header_translations.get(header, header)
            )
        translated_headers += [
            'Is decoy',
            'Retention Time (s)',
            header_translations.get(' E-value', ' E-value'),
            header_translations.get(' P-value', ' P-value'),
            # 'Raw data location'
        ]
        print('[ PARSING  ] Loading unformatted OMSSA results ...')
        for line_dict in csv_dict_reader_object:
            cached_omssa_output.append( line_dict )
        result_file.close()

        #
        result_file = open( self.params['translations']['output_file_incl_path'], 'w')
        csv_dict_writer_object = csv.DictWriter(
            result_file,
            fieldnames = translated_headers
        )
        csv_dict_writer_object.writeheader()
        #
        # self.parse_fasta()
        # already_seen_protein_scan_start_stop_combos = set()
        # database = self.params['translations']['database']
        for m in cached_omssa_output:
            tmp = {}
            for header in headers:
                translated_header = header_translations.get(
                    header,
                    header
                )
                tmp[ translated_header ] = m[ header ]
            tmp['Sequence'] = tmp['Sequence'].upper()

            # returned_peptide_regex_list = self.peptide_regex(
            #     self.params['database'],
            #     tmp['proteinacc_start_stop_pre_post_;'],
            #     tmp['Sequence']
            # )

            translated_mods = []
            if tmp['Modifications'] != '':
                splitted_Modifications = tmp['Modifications'].split(',')
                for mod in splitted_Modifications:
                    omssa_name, position = mod.split(':')
                    omssa_name  = omssa_name.strip()
                    position    = position.strip()
                    unimod_name = self.lookups[ omssa_name ]['name']
                    if position.strip() == '1':
                        # print( self.lookups[ omssa_name ] )
                        for target in self.lookups[ omssa_name ]['aa_targets']:
                            if 'N-TERM' in target.upper():
                                position = '0'
                    translated_mods.append(
                        '{0}:{1}'.format(
                            unimod_name,
                            position
                        )
                    )

            tmp['Modifications'] = ';'.join( translated_mods )

            # for protein in returned_peptide_regex_list:
            #     for pep_regex in protein:
            #         start, stop, pre_aa, post_aa, returned_protein_id = pep_regex
            #         protein_scan_start_stop = (
            #             returned_protein_id,
            #             tmp['Spectrum Title'],
            #             start,
            #             stop
            #         )
            #         if protein_scan_start_stop in already_seen_protein_scan_start_stop_combos:
            #             continue
            #         else:
            #             already_seen_protein_scan_start_stop_combos.add(protein_scan_start_stop)

            #         tmp['Start'] = start
            #         tmp['Stop'] = stop

            #         tmp['proteinacc_start_stop_pre_post_;'] = '{0}_{1}_{2}_{3}_{4}'.format(
            #             tmp['proteinacc_start_stop_pre_post_;'],
            #             start,
            #             stop,
            #             pre_aa,
            #             post_aa
            #         )

            #         if self.params['decoy_tag'] in tmp['proteinacc_start_stop_pre_post_;']:
            #             tmp['Is decoy'] = 'true'
            #         else:
            #             tmp['Is decoy'] = 'false'
            csv_dict_writer_object.writerow( tmp )
        return


