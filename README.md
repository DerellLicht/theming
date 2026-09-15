###  generating `colors.json` file for `PrettyReMark` markdown reader

Notes:
- all the theme files in `themes` folder, were copied from `notepad++`,
  in accordance with their license file.
  
- all management of the colors files are handled by `do_color.cmd`  
```
USAGE:
    do_color [command]
    [command] = [build] [test] [push] [pull]
    do_color [command] <theme_file_name> [<test_selection_file>]

    Exactly *one* [command] is required
 DETAILS:

ARGUMENTS
   <theme_file_name>  [mandatory]
   <test_selection_file>  [optional]

   Examples:
   do_color build themes\Zenburn.xml
   do_color test themes\Zenburn.xml select_test.json
   do_color push choco
   do_color pull
   do_color swatch themes\Monokai.xml

 NOTES:
   push: This expects only the theme name, located in colors folder
         This will be expanded to [colors\colors.<theme_name>.json]

   pull: and build:
      These will result in a [colors.json] file in current folder.
      They will need to be renamed to colors.<theme_name>.json
      and then be moved to [colors] folder

```

Caution when using `do_color push` ...
`PrettyReMark` should be closed when running this command;
The viewer only reads this file at program startup, and it might over-write your
changes if settings are otherwise changed while it is running.
