.. code-block:: python

	#!/usr/bin/env python3.4
	# encoding: utf-8
	
	import ursgal
	import os
	
	
	def main():
	    '''
	    Examples script for filtering validated results for a PEP <= 0.01 and
	    remove all decoys.
	
	    usage:
	        ./filter_csv_validation_example.py
	
	
	    Will produce a file with only target sequences with a posterior error
	    probability of lower or equal to 1 percent
	    '''
	    params = {
	        'csv_filter_rules': [
	            ['PEP', 'lte', 0.01],
	            ['Is decoy', 'equals', 'false']
	        ]
	    }
	
	    csv_file_to_filter = os.path.join(
	        os.pardir,
	        'example_data',
	        'misc',
	        'filter_csv_validation_example_omssa_2_1_9_unified_percolator_2_08_validated.csv'
	    )
	    uc = ursgal.UController(
	        params = params
	    )
	
	    filtered_csv = uc.filter_csv(
	        input_file = csv_file_to_filter,
	
	    )
	
	
	if __name__ == '__main__':
	    main()
