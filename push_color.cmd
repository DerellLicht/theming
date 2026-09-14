@if /I "%~1"=="" goto :usage
@goto :build

:usage
   @echo USAGE:
   @echo     push_color ^<colors.ColorName.json^>
   @echo     Copies color file to colors.json in PrettyReMark config folder
   @echo.
   @echo ARGUMENTS
   @echo    ^<colors.ColorName.json^>  [mandatory]
   @echo.
   @echo    Example: 
   @echo    push_color colors.HotFudgeSundae.json
   @goto :eof

:build
   @IF NOT EXIST "%~1" (
      @goto :usage
   )
   copy %1 C:\Users\dan7m\AppData\Roaming\PrettyReMark\colors.json
   @goto :eof

