#!/usr/bin/env python3.4

import ursgal
import os.path
import importlib.machinery
import sys
from pprint import pprint


class naive_bayes_1_0_0( ursgal.UNode ):
    '''
    naive_bayes_1_0_0 UNode
    '''
    META_INFO = {
        'engine_type'    : {
            'controller'        : False,
            'converter'         : False,
            'validation_engine' : False,
            'search_engine'     : False,
            'meta_engine'       : True,
        },
        'input_types'               : ['.csv'],
        'output_extension'          : '.csv',
        'create_own_folder'         : False,
        'citation' : 'Combines PEP scores from different search engines '\
            'using naive Bayes (see i.e. '\
            'http://www.paulgraham.com/naivebayes.html)',
        'include_in_git'            : True,
        'in_development'            : False,
        'engine': {
            'platform_independent' : {
                'arc_independent' : {
                    'exe'     : 'naive_bayes_1_0_0.py',
                },
            },
        },
        'citation'                  : 'Kremer, L. P. M., Leufken, J., '\
            'Oyunchimeg, P., Schulze, S. & Fufezan, C. (2016) '\
            'Ursgal, Universal Python Module Combining Common Bottom-Up '\
            'Proteomics Tools for Large-Scale Analysis. '\
            'J. Proteome res. 15, 788-794.',
    }
    def __init__(self, *args, **kwargs):
        super(naive_bayes_1_0_0, self).__init__(*args, **kwargs)
        pass


    def preflight( self ):
        '''
        Building the list of parameters that will be passed to the
        naive_bayes_1_0_0 main function.

        These parameters are stored in self.command_dict

        Returns:
                None
        '''
        input_file_list_for_bayes = []
        search_engine_list_for_bayes = []
        # these must have the same order!

        for input_file_dict in self.params["input_file_dicts"]:
            input_file_path = os.path.join(
                input_file_dict['dir'],
                input_file_dict['file']
            )
            input_file_list_for_bayes.append(input_file_path)
            search_engine = input_file_dict["last_engine"]
            search_engine_list_for_bayes.append(search_engine)

        features_that_define_unique_psm = \
            ['Sequence', 'Modifications', 'Spectrum Title']

        output_csv_full_path = os.path.join(
            self.params['output_dir_path'],
            self.params['output_file'],
        )

        self.command_dict = {
            'input_csvs': input_file_list_for_bayes,
            'input_engines': search_engine_list_for_bayes,
            'output_csv': output_csv_full_path,
            'columns_for_grouping': features_that_define_unique_psm,
            'input_sep': ',',  # input csv separating char
            'output_sep': ',',  # output csv separating char
            'join_sep': ';',  # char to join multiple values in same field
            'pep_colname': 'PEP',
        }

    def _execute( self ):
        '''
        Executing the combine_FDR_0_1 main function with parameters
        that were defined in preflight (stored in self.command_dict)

        The main function is imported and then executed using the
        parameters from command_dict.

        Returns:
                None
        '''
        naive_bayes_main = self.import_engine_as_python_function()

        print('''

Executing main() function from {scriptpath} with the following parameters:

>>> {script}.main(
...     input_csvs = {input_csvs},
...     input_engines = {input_engines},
...     output_csv = '{output_csv}',
...     columns_for_grouping = {columns_for_grouping},
...     input_sep = '{input_sep}',
...     output_sep = '{output_sep}',
...     join_sep = '{join_sep}',
...     pep_colname = '{pep_colname}',
... )

        '''.format(
            scriptpath = os.path.relpath( self.exe ),
            script     = os.path.basename( self.exe ),
            **self.command_dict
            )
        )

        # executing main function of the naive bayes script
        naive_bayes_main(
            input_csvs = self.command_dict['input_csvs'],
            input_engines = self.command_dict['input_engines'],
            output_csv = self.command_dict['output_csv'],
            columns_for_grouping = self.command_dict['columns_for_grouping'],
            input_sep = self.command_dict['input_sep'],
            output_sep = self.command_dict['output_sep'],
            join_sep = self.command_dict['join_sep'],
            pep_colname = self.command_dict['pep_colname'],
        )
