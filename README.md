# EIRepeat - EI Repeat Identification Pipeline

EIRepeat is an easy to use pipeline to identify repeats from the genome. 

EIRepeat utilises below tools to identify repeats:
1. RepeatModeler v1.0.11 - https://www.repeatmasker.org/RepeatModeler
2. RepeatMasker v4.0.7 - http://www.repeatmasker.org/RepeatMasker
3. RED v22052015 - http://toolsmith.ens.utulsa.edu - [Paper here](https://doi.org/10.1186/s12859-015-0654-5)

## Getting Started

To configure EIRepeat you need:

* EIRepeat source code
* software dependencies

To obtain the EIRepeat source code from GitHub, please execute:

```console
git clone https://github.com/ei-corebioinformatics/eirepeat
```

### Prerequisites

For ease of development, Singularity is recommended to install the dependencies
```console
RepeatModeler v1.0.11
RepeatMasker v4.0.7
RED v22052015 http://toolsmith.ens.utulsa.edu/red/data/DataSet1Src.tar.gz
SeqKit v2.1.0
TransposonPSI v08222010
BLAST v2.6.0
Bedtools v2.25.0
``` 

### Installing

First obtain the source code using

```console
git clone https://github.com/ei-corebioinformatics/eirepeat
cd eirepeat
```

To install, simply use from your current pip environment:
```console
version=1.0.0 && python setup.py bdist_wheel \
&& pip install --prefix=/path/to/software/eirepeat/${version}/x86_64 -U dist/*whl
```
Also make sure that both PATH and PYTHONPATH enviroments are updated 
```console
export PATH=/path/to/software/eirepeat/${version}/x86_64/bin:$PATH
export PYTHONPATH=/path/to/software/eirepeat/${version}/x86_64/lib/python3.9/site-packages
```

## Running EIRepeat

### Get help
```console
$ eirepeat --help
usage: EI Repeat [-h] [-v] {configure,run} ...

EI Repeat Identification Pipeline

positional arguments:
  {configure,run}
    configure      see `configure -h`
    run            see `run -h`

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
```

EIRepeat configure
```console
$ eirepeat configure --help
usage: EI Repeat configure [-h] --species SPECIES [--run_red_repeats] [--close_reference CLOSE_REFERENCE] [--organellar_fasta ORGANELLAR_FASTA] [-o OUTPUT] [-f] fasta

positional arguments:
  fasta                 Provide fasta file

optional arguments:
  -h, --help            show this help message and exit
  --species SPECIES     Provide species name. Please use the file here to identify the species. Also, check the NCBI taxonomy to identify the correct species option - https://www.ncbi.nlm.nih.gov/taxonomy: /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-
                        packages/eirepeat/etc/queryRepeatDatabase.tree.txt (default: None)
  --run_red_repeats     Enable this option to generate RED repeats, in addition (default: False)
  --close_reference CLOSE_REFERENCE
                        Provide a close reference protein CDS fasta to mask the RepeatModeler fasta. Try to extract just protein coding models and remove any models identified as repeat associated from this file (default: None)
  --organellar_fasta ORGANELLAR_FASTA
                        Provide organellar chloroplast|mitrochondrial nucleotide fasta to mask the RepeatModeler fasta. Use provided script ncbi_download.py to download this fasta file from NCBI (default: None)
  -o OUTPUT, --output OUTPUT
                        Provide output directory (default: /ei/cb/development/kaithakg/eirepeat/dev/test_run1/output)
  -f, --force-reconfiguration
                        Force reconfiguration (default: False)
```
         
EIRepeat run
```console
$ eirepeat run --help
usage: EI Repeat run [-h] --run_config RUN_CONFIG [--hpc_config HPC_CONFIG] [--jobs JOBS] [--latency_wait LATENCY_WAIT] [--no_posting] [--verbose] [-np] jira

positional arguments:
  jira                  Provide JIRA id for posting job summary. E.g., PPBFX-611

optional arguments:
  -h, --help            show this help message and exit
  --run_config RUN_CONFIG
                        Provide run configuration YAML. Run 'eirepeat configure -h' to generate the run configuration YAML file. (Description template file is here: /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-packages/eirepeat/etc/run_config.yaml)
  --hpc_config HPC_CONFIG
                        Provide HPC configuration YAML (default: /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-packages/eirepeat/etc/hpc_config.json)
  --jobs JOBS, -j JOBS  Use at most N CPU cluster/cloud jobs in parallel (default: 100)
  --latency_wait LATENCY_WAIT
                        Wait given seconds if an output file of a job is not present after the job finished (default: 120)
  --no_posting          Use this flag if you are testing and do not want to post comments to JIRA tickets (default: False)
  --verbose             Verbose mode for debugging (default: False)
  -np, --dry_run        Dry run (default: False)
```

### Execution

### eirepeat configure
There are mainly four ways you can configure EIRepeat to run, depending upon the types of evidence you have.
#### 1. Using just the genome 
```console
eirepeat configure --output run1 --species Insecta honey_bee.genome.fasta
Running configure..

Great! Created run_config file: '/path/to/run1/run_config.yaml'

```

#### 2. Using just the genome and organellar fasta
```console
eirepeat configure --output run2 --species Insecta \
    --organellar_fasta Bombus_ORGN_10433_mitochondrion.complete_record.fasta \
    honey_bee.genome.fasta
Running configure..

Great! Created run_config file: '/path/to/run2/run_config.yaml'

```
NOTE:
You can use the script `ncbi_download.py` to download organellar fasta file from NCBI, please see below a real eample where we download both `mitochondrion` and `chloroplast` fasta for all `eudicotyledons`.
Please make sure that you have external internet access before executing this script.

```
ncbi_download.py -e first.last@domain.xx.xx '"eudicotyledons"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])' eudicotyledons.genetic_compartments.849434.07Dec2021.Entrez.sequence.fasta
```

#### 3. Using just the genome and close reference protein coding CDS fasta
```console
eirepeat configure --output run3 --species Insecta \
    --close_reference GCF_000214255.1_Bter_1.0_cds_from_genomic.nonTE.fa \
    honey_bee.genome.fasta
Running configure..

Great! Created run_config file: '/path/to/run3/run_config.yaml'

```
NOTE:
Here, make sure that the CDS fasta file you provide with --close_reference is only the protein coding CDS models.
What I would do here is that:
1. Extract only models with `gene_biotype` and `transcript_biotype` marked as `protein_coding`
2. The if function annotation is available remove any repeat associated models, for example, the `grep` command `grep -v "\(transpos\|helicas\)"` should suffice.


#### 4. Using just the genome, the organellar fasta and close reference protein coding CDS fasta [RECOMMENDED]
```console
eirepeat configure --output run4 --species Insecta \
    --organellar_fasta Bombus_ORGN_10433_mitochondrion.complete_record.fasta \
    --close_reference GCF_000214255.1_Bter_1.0_cds_from_genomic.nonTE.fa \
    honey_bee.genome.fasta
Running configure..

Great! Created run_config file: '/path/to/run4/run_config.yaml'

```
NOTE:
Before running this, make sure that we do follow the notes under section 2 and 3 to prepare the inputs


### eirepeat run
EIRepeat run command is quite simple. All the above four runs can be executed like below
```console
eirepeat run --run_config run1/run_config.yaml PPBFX-611
```
NOTE:
I would recomment to run the above command as a cluster job to avoid terminal connection drop-outs.
Below is an example HPC command we use for SLURM job scheduler 
```console
cd work_dir
sbatch --mail-type=END --mail-user=first.last@domain.xx.xx \
    -p ei-medium -c 2 --mem 20G -J eirepeat-run1 -o out_eirepeat-run1.%N.%j.log \
    --wrap "source eirepeat-1.0.0 && \
    /usr/bin/time -v eirepeat run --run_config run1/run_config.yaml PPBFX-611"
```

## Output
Once the job completes successfully, we should see the summary below in the log file. 
```console
...
...
EIREPEAT completed successfully!

The output directory is below:
/path/to/run1

RepeatMasker
RepeatMasker output using RepeatMasker library 'Insecta' repeats (low-complexity):
/path/to/run1/RepeatMasker_low/genome.fa.out.gff
/path/to/run1/RepeatMasker_low/genome.fa.out.gff3

RepeatMasker output using RepeatMasker library 'Insecta' repeats (interspersed):
/path/to/run1/RepeatMasker_interspersed/genome.fa.out.gff
/path/to/run1/RepeatMasker_interspersed/genome.fa.out.gff3

RepeatMasker output using RepeatModeler repeats (interspersed):
/path/to/run1/RepeatMasker_interspersed_repeatmodeler/genome.fa.out.gff
/path/to/run1/RepeatMasker_interspersed_repeatmodeler/genome.fa.out.gff3


Main output files
All repeats (low + interspersed):
/path/to/run1/all_repeats.raw.out.gff
/path/to/run1/all_repeats.gff3

All interspersed repeats (interspersed):
/path/to/run1/all_interspersed_repeats.raw.out.gff
/path/to/run1/all_interspersed_repeats.gff3


Additional repeats:
RED Repeats
/path/to/run1/red/genome.rpt.gff3

EI Repeat Summary Stats:
All repeats (low + interspersed)
Total Sequences                 240
Total Bases                       2.58641e+08
Total Masked bases                4.66707e+07
Total Percentage Bases Masked    18.0446

All interspersed repeats (interspersed)
Total Sequences                 240
Total Bases                       2.58641e+08
Total Masked bases                4.11962e+07
Total Percentage Bases Masked    15.9279

RED repeats
Total Sequences                 240
Total Bases                       2.58641e+08
Total Masked bases                7.83649e+07
Total Percentage Bases Masked    30.2987


Storage details
Output directory:
3.8G    /path/to/run1
3.8G    total

```

## Workflow
TBD


## Reporting suggestions/issues
Please raise a GitHub issue for any suggestions or issues you have.

Alternatively, I can be contacted at:
Gemy.Kaithakottil@earlham.ac.uk or 
gemygk@gmail.com
