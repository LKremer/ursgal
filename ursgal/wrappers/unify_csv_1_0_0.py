#!/usr/bin/env python3.4
import ursgal
import importlib
import os
import sys
import pickle


class unify_csv_1_0_0( ursgal.UNode ):
    """unify_csv_1_0_0 UNode"""
    META_INFO = {
        'engine_type' : {
            'search_engine' : False,
            'converter'     : True
        },
        'output_extension'  : '.csv',
        'output_suffix'     : 'unified',
        'input_types'       : ['.csv'],
        'include_in_git'    : True,
        'in_development'    : True,
        'utranslation_style': 'unify_csv_style_1',
        'engine': {
            'platform_independent' : {
                'arc_independent' : {
                    'exe' : 'unify_csv_1_0_0.py',
                },
            },
        },
        'citation'          : 'Kremer, L. P. M., Leufken, J., '\
            'Oyunchimeg, P., Schulze, S. & Fufezan, C. (2016) '\
            'Ursgal, Universal Python Module Combining Common Bottom-Up '\
            'Proteomics Tools for Large-Scale Analysis. '\
            'J. Proteome res. 15, 788-794.',
    }

    def __init__(self, *args, **kwargs):
        super(unify_csv_1_0_0, self).__init__(*args, **kwargs)

    def _execute( self ):
        '''
        Result files from search engines are unified
        to contain the same informations in the same style

        Input file has to be a .csv

        Creates a _unified.csv file and returns its path

        '''
        print('[ -ENGINE- ] Executing conversion ..')
        self.time_point(tag = 'execution')
        unify_csv_main = self.import_engine_as_python_function()
        if self.params['output_file'].lower().endswith('.csv') is False:
            raise ValueError('Trying to unify a non-csv file')

        output_file = os.path.join(
            self.params['output_dir_path'],
            self.params['output_file']
        )
        input_file  = os.path.join(
            self.params['input_dir_path'],
            self.params['input_file']
        )

        scan_rt_lookup_path = self.meta_unodes['ucontroller'].scan_rt_lookup_path

        assert os.path.isfile( scan_rt_lookup_path ), """
Could not load RT lookup dict from this location: {0}
        """.format( scan_rt_lookup_path )

        scan_rt_lookup_dict = pickle.load(
            open( scan_rt_lookup_path, 'rb' )
        )

        # find the last search/denovo engine:
        last_engine = self.get_last_engine(
            history = self.stats['history'],
        )

        last_search_engine_colname = self.UNODE_UPARAMS['validation_score_field']['uvalue_style_translation'][last_engine]

        tmp_files = unify_csv_main(
            input_file      = input_file,
            output_file     = output_file,
            scan_rt_lookup  = scan_rt_lookup_dict,
            params          = self.params,
            search_engine   = last_engine,
            score_colname   = last_search_engine_colname,
            upeptide_mapper = self.upeptide_mapper
        )
        for tmp_file in tmp_files:
            self.created_tmp_files.append(tmp_file)

        self.print_execution_time(tag='execution')
        return output_file
