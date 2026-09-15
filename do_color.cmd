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
@if /I "%~1"=="swatch" goto :swatch

:usage
   @echo USAGE:
   @echo     do_color [command]
   @echo     [command] = [build] [test] [push] [pull] [swatch]
   @echo     do_color [command] ^<theme_file_name^> [^<test_selection_file^>]
   @echo.
   @echo     Exactly *one* [command] is required
   @echo. DETAILS:
   @echo.
   @echo ARGUMENTS
   @echo    ^<theme_file_name^>  [mandatory]
   @echo    ^<test_selection_file^>  [optional, only for [test] command]
   @echo.
   @echo    Examples: 
   @echo    do_color build themes\Zenburn.xml
   @echo    do_color test themes\Zenburn.xml select_test.json
   @echo    do_color push choco
   @echo    do_color pull
   @echo    do_color swatch themes\Monokai.xml
   @echo.
   @echo. NOTES:
   @echo    push: This expects only the theme name, located in colors folder
   @echo          This will be expanded to [colors\colors.^<theme_name^>.json]
   @echo.
   @echo    pull: and build: 
   @echo       These will result in a [colors.json] file in current folder.
   @echo       They will need to be renamed to colors.^<theme_name^>.json
   @echo       and then be moved to [colors] folder
   @echo.
   @goto :eof

:build
   @IF NOT EXIST "%~2" GOTO :usage
   python theme_to_colors.py %2
   @goto :eof

:test
   @IF NOT EXIST "%~2" GOTO :usage
   python theme_to_colors.py %2 %3
   @goto :eof

:push
   SET "target=colors\colors.%2.json"
   @IF NOT EXIST "%target%" GOTO :usage
   @COPY "%target%" "%APPDATA%\PrettyReMark\colors.json"
   @goto :eof

:pull
   @copy %APPDATA%\PrettyReMark\colors.json .
   @echo colors.json needs to be renamed to something else
   @goto :eof

:swatch
   @IF NOT EXIST "%~2" GOTO :usage
   python theme_swatch.py %2
   move themes\*.html swatches
   