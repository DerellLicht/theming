::  This will be an example file that demonstrates flow-control options
::  To see An A-Z Index of Windows CMD commands, visit:
::  https://ss64.com/nt/
::  %1 = command
::  %2 = theme file
::  %3 = select file [optional, only for [test]

@if /I "%~1"=="" goto :usage
@if /I "%~1"=="build" goto :build
@if /I "%~1"=="test" goto :test
@if /I "%~1"=="push" goto :push
@if /I "%~1"=="pull" goto :pull

:usage
   @echo USAGE:
   @echo     do_color [command]
   @echo     [command] = [build] [test] [push] [pull]
   @echo     do_color ^<theme_file_name^> [^<test_selection_file^>]
   @echo.
   @echo     Exactly *one* [command] is required
   @echo. DETAILS:
   @echo.
   @echo.
   @echo ARGUMENTS
   @echo    ^<theme_file_name^>  [mandatory]
   @echo    ^<test_selection_file^>  [optional]
   @echo.
   @echo    Examples: 
   @echo    do_color build themes\Zenburn.xml
   @echo    do_color test themes\Zenburn.xml select_test.json
   @echo    do_color push colors\colors.choco.json
   @echo    do_color pull
   @goto :eof

:build
   @if /I "%~2"=="" goto :usage
   python theme_to_colors.py %2
   @goto :eof

:test
   @if /I "%~2"=="" goto :isage 
   python theme_to_colors.py %1 %2
   @goto :eof

:push
   @IF NOT EXIST "%~2" (
      @goto :usage
   )
   copy %2 C:\Users\dan7m\AppData\Roaming\PrettyReMark\colors.json
   @goto :eof

:pull
   @copy C:\Users\dan7m\AppData\Roaming\PrettyReMark\colors.json .
   @echo colors.json needs to be renamed to something else
   @goto :eof

