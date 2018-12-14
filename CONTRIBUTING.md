Important:

    input data should be put into the "input_data" folder, but have the file(s) ignored by git (use gitignore); I would suggest passing the files via WeTransfer or similar. I have the Kratos and FeFlow; please share the OpenFoam results

    report files are created in the "reports" folder

    for testing out new developments please use the main file call "python3 evaluate_results.py"

    for evaluating all (with mode calculation on and default nr of blocks = 6) call "python3 evaluate_results.py --calculate_mode True --run_test False"


    usage of flags - as defined in utilities/other_utilitites.py -> get_custom_parser_settings()
        run test or note:                  -rt or --run_test
        calculate mode or not:             -cm or --calculate_mode
        number of blocks for block maxima: -nb or --number_of_blocks
        how to calculate cp:               -cpm or --cp_mode

    example: python3 evaluate_results.py -rt 'false' -cm 'true' -cpm 'trad'
