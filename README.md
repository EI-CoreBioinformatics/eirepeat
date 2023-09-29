# EIRepeat - EI Repeat Identification Pipeline
Gemy George Kaithakottil, David Swarbreck

## 1 Description

EIRepeat is an easy to use pipeline to identify repeats from the genome. 

EIRepeat utilises below tools to identify repeats:
1. RepeatModeler v1.0.11 - https://www.repeatmasker.org/RepeatModeler
2. RepeatMasker v4.0.7 - http://www.repeatmasker.org/RepeatMasker
3. RED v22052015 - http://toolsmith.ens.utulsa.edu - [Paper here](https://doi.org/10.1186/s12859-015-0654-5)


## 2 Workflow
![Alt text](/eirepeat/doc/eirepeat_diagram.png)
Figure 1. The overview of Earlham Institute Repeat Identification Pipeline (EIRepeat)

## 3 Getting Started

To configure EIRepeat you need:

* EIRepeat source code
* software dependencies

To obtain the EIRepeat source code from GitHub, please execute:

```console
git clone https://github.com/ei-corebioinformatics/eirepeat
```

### 3.1 Prerequisites

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

### 3.2 Installing

First obtain the source code using

```console
git clone https://github.com/ei-corebioinformatics/eirepeat
cd eirepeat
```

To install, simply use from your current pip environment:
```console
version=1.3.4 && python setup.py bdist_wheel \
&& pip install --prefix=/path/to/software/eirepeat/${version}/x86_64 -U dist/*whl
```
Or use Python [Poetry](https://python-poetry.org/)
```console
version=1.3.4 && poetry build \
&& pip install --prefix=/path/to/software/eirepeat/${version}/x86_64 -U dist/*whl
```
Also, make sure that both PATH and PYTHONPATH environments are updated and DRMAA_LIBRARY_PATH points to the DRMAA installation
```console
export PATH=/path/to/software/eirepeat/${version}/x86_64/bin:$PATH
export PYTHONPATH=/path/to/software/eirepeat/${version}/x86_64/lib/python3.11/site-packages
export DRMAA_LIBRARY_PATH=/path/to/software/slurm-drmaa/1.1.4/x86_64/lib/libdrmaa.so
```

## 4 Running EIRepeat

### 4.1 Get help
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
usage: EI Repeat configure [-h] --species SPECIES [--run_red_repeats] [--close_reference CLOSE_REFERENCE] [--organellar_fasta ORGANELLAR_FASTA] [--jira JIRA] [-o OUTPUT] [-f] fasta

positional arguments:
  fasta                 Provide fasta file

optional arguments:
  -h, --help            show this help message and exit
  --species SPECIES     Provide species name. Please use the file here to identify the species. Also, check the NCBI taxonomy to identify the correct species option - https://www.ncbi.nlm.nih.gov/taxonomy:
                        /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-packages/eirepeat/etc/queryRepeatDatabase.tree.txt (default: None)
  --run_red_repeats     Enable this option to generate RED repeats, in addition (default: False)
  --close_reference CLOSE_REFERENCE
                        Provide a close reference protein CDS fasta to mask the RepeatModeler fasta. Try to extract just protein coding models and remove any models identified as repeat associated from this file (default: None)
  --organellar_fasta ORGANELLAR_FASTA
                        Provide organellar chloroplast|mitrochondrial nucleotide fasta to mask the RepeatModeler fasta. Use provided script ncbi_download to download this fasta file from NCBI (default: None)
  --jira JIRA           Provide JIRA id for posting job summary. E.g., PPBFX-611 (default: None)
  -o OUTPUT, --output OUTPUT
                        Provide output directory (default: /ei/cb/development/kaithakg/eirepeat/dev/output)
  -f, --force-reconfiguration
                        Force reconfiguration (default: False)
```
         
EIRepeat run
```console
$ eirepeat run --help
usage: EI Repeat run [-h] [--hpc_config HPC_CONFIG] [--jobs JOBS] [--latency_wait LATENCY_WAIT] [--no_posting] [--verbose] [-x] [-np] run_config

positional arguments:
  run_config            Provide run configuration YAML. Run 'eirepeat configure -h' to generate the run configuration YAML file. (Description template file is here: /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-
                        packages/eirepeat/etc/run_config.yaml)

optional arguments:
  -h, --help            show this help message and exit
  --hpc_config HPC_CONFIG
                        Provide HPC configuration YAML (default: /ei/software/cb/eirepeat/dev/x86_64/lib/python3.9/site-packages/eirepeat/etc/hpc_config.json)
  --jobs JOBS, -j JOBS  Use at most N CPU cluster/cloud jobs in parallel (default: 100)
  --latency_wait LATENCY_WAIT
                        Wait given seconds if an output file of a job is not present after the job finished (default: 120)
  --no_posting          Use this flag if you are testing and do not want to post comments to JIRA tickets (default: False)
  --verbose             Verbose mode for debugging (default: False)
  -x, --exclude_hosts   Enable excluding a specific list of hosts specified in the --hpc_config 'exclude' section (default: False)
  -np, --dry_run        Dry run (default: False)
```

### 4.2 Execution

### 4.2.1 eirepeat configure
There are mainly four ways you can configure EIRepeat to run, depending upon the types of evidence you have.
#### 1. Using just the genome 
```console
eirepeat configure --output run1 --species Insecta honey_bee.genome.fasta
Running configure..

Great! Created run_config file: '/path/to/run1/run_config.yaml'

```
:exclamation: **IMPORTANT NOTE:**  
In all cases, it is **recommended** that the genome fasta headers be shorter than <50 characters otherwise RepeatModeler might error, like:
```
FastaDB::_cleanIndexAndCompact(): Fasta file contains a sequence identifier which is too long ( max id length = 50 )
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
You can use the script `ncbi_download` to download organellar fasta file from NCBI, please see below a real eample where we download both `mitochondrion` and `chloroplast` fasta for all `eudicotyledons`.
Please make sure that you have external internet access before executing the `ncbi_download` script.

```console
ncbi_download \
  -e first.last@domain.xx.xx \
  '"eudicotyledons"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])' \
  eudicotyledons.genetic_compartments.849434.07Dec2021.sequence.fasta
```
 
In the above example command, I use the name `eudicotyledons.genetic_compartments.849434.07Dec2021.sequence.fasta`
just to keep a record of the data for our own reference, where:
 - eudicotyledons : is the organism name
 - 849434         : is the number of hits received for [query](https://www.ncbi.nlm.nih.gov/nuccore/?term=%22eudicotyledons%22%5BOrganism%5D+AND+(mitochondrion%5Bfilter%5D+OR+chloroplast%5Bfilter%5D)) on 07Dec2021 from NCBI nuccore. This number might differ on another date for your query.
 - 07Dec2021      : is the date data was downloaded

You can call the output fasta with any name.




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
2. And if any functional annotation is available then remove any repeat associated models, for example, the `grep` command `grep -v "\(transpos\|helicas\)"` should get you all the models that are repeat associated and then remove them from the fasta.  
  If you have [SeqKit](https://bioinf.shenwei.me/seqkit/) toolkit available in your PATH, we can do this in one step, for example, `seqkit grep -v -r -p 'transpos|helicas' {input.fasta} -o {output.fasta}`


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


### 4.2.2 eirepeat run
EIRepeat run command is quite simple. All the above four runs can be executed like below
```console
eirepeat run run1/run_config.yaml
```
NOTE:  
I would recomment to run the above command as a cluster job to avoid terminal connection drop-outs.
Below is an example HPC command we use for SLURM job scheduler 
```console
cd work_dir
sbatch --mail-type=END --mail-user=first.last@domain.xx.xx \
    -p ei-medium -c 2 --mem 20G -J eirepeat-run1 -o out_eirepeat-run1.%N.%j.log \
    --wrap "source eirepeat-1.0.0 && \
    /usr/bin/time -v eirepeat run run1/run_config.yaml"
```

## 5. Output
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


Additional repeats:                                  - with --run_red_repeats option
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

RED repeats                                          - with --run_red_repeats option
Total Sequences                 240
Total Bases                       2.58641e+08
Total Masked bases                7.83649e+07
Total Percentage Bases Masked    30.2987


Storage details
Output directory:
3.8G    /path/to/run1
3.8G    total

```

## 6 Troubleshooting
### SLURM specific
If there are certain cluster nodes/hosts you would like to exclude when running the pipeline, you can update the `--hpc_config` JSON file in the `exclude` field.
Once you have updated the HPC config JSON file, you can provide that to the eirepeat pipeline, like `eirepeat run --exclude_hosts`.  
**Remember** to use `--exclude_hosts` when you do this.

## 7 Reporting suggestions/issues
Please raise a GitHub issue for any suggestions or issues you may have.

Alternatively, I can be contacted at:
Gemy.Kaithakottil@earlham.ac.uk or 
gemygk@gmail.com
