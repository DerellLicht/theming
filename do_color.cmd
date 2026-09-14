::  This will be an example file that demonstrates flow-control options
::  To see An A-Z Index of Windows CMD commands, visit:
::  https://ss64.com/nt/

@if /I "%~1"=="" goto :usage
@if /I "%~2"=="" goto :build_default
goto :build_test

:usage
   @echo USAGE:
   @echo     do_color ^<theme_file_name^> [^<test_selection_file^>]
   @echo.
   @echo ARGUMENTS
   @echo    ^<theme_file_name^>  [mandatory]
   @echo    ^<test_selection_file^>  [optional]
   @echo.
   @echo    Example: 
   @echo    do_color themes\Zenburn.xml
   @goto :eof

:build_default
   python theme_to_colors.py %1
   @goto :eof

:build_test
   python theme_to_colors.py %1 %2
   @goto :eof

