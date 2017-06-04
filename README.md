# mcg

Simple Markov chain text generator written in Python.

## Usage

    usage: mcg.py [-h] [-i words] [-l number] [-n number] [-s] [-c] [file]

    Create similar texts using Markov processes.

    positional arguments:
      file        input file

    optional arguments:
      -h, --help  show this help message and exit
      -i word(s)  initial words of the generated text
      -l number   length of the produced text in words
      -n number   order of the Markov chain
      -s          show the tranisition table and exit
      -c          read the source as a cyclic sequence

## License

mcg is licensed under the BSD-2 clause license. See [LICENSE](https://github.com/bozbalci/mcg/blob/master/LICENSE) for more information.
