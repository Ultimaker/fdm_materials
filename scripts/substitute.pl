#!/usr/bin/perl
use strict;
use File::Find; # for recursion
no warnings 'File::Find';

#my @tmp;
my $real = shift;
my $filter = shift;
my $file = shift;
my $fileFilter;
my $change = 0;
my %n;

sub Color(;$$);
my %ColorTypes = (
    normal      => '0',
    bold        => '1',
    dark        => '2',
    _           => '4',
    block       => '7',
    passwd      => '8',
    '-'         => '9',
    bg_white    => '40',
    bg_red      => '41',
    bg_green    => '42',
    bg_yellow   => '43',
    bg_blue     => '44',
    bg_magenta  => '45',
    bg_cyan     => '46',
    bg_gray     => '47');
my %Colors  = (
    normal      => '0',
    bold        => '29',#white
    black       => '30',
    red         => '31',
    green       => '32',
    yellow      => '33',
    blue        => '34',
    magenta     => '35',
    cyan        => '36',
    bg_white    => '40',
    bg_red      => '41',
    bg_green    => '42',
    bg_yellow   => '43',
    bg_blue     => '44',
    bg_magenta  => '45',
    bg_cyan     => '46',
    bg_grey     => '47');
my $red   = Color("normal","red");
my $green = Color("normal","green");
my $norm  = Color();

print "filter \"$filter\"\n";

if (not defined $file)
{
    usage();
}

if ( -e $file and -d $file )
{
    print "will recuse into dir $file\n";
    recursive($file, shift);
}
elsif ( -e $file )
{
  print "will hande list of file(s)\n";
  while ($file) 
  {
    &write(&read);
    $file = shift;
  }
}
else
{
    usage();
}
# read data & substitute naar array
sub read($)
{
  my @data;
  open (IN, $file);
   local $/;
    while (<IN>) 
    {
      my $tmp = $_;
      eval "$filter";
      die $@ if $@;
      
      if ($real eq 'y') {
	  $change = 1 if ($_ ne $tmp);
	  push (@data, "$_");
      }
      else 
      {
          if ($_ ne $tmp)
	  {

#	      print "Before $tmp";
#	      sleep 5;
	      print "$_\n press enter to continue...";$|++;
              { local $/ = "\n"; <STDIN>; }
	      $change = 1;
	  }
	  push (@data, "$tmp");
      }
    }
  close IN;
  return @data;
}

sub write {
    if ($change)
    {
	open (WRITE, ">$file") or die "bad pipe to file '$file' $!\n";
	print WRITE @_;
	close WRITE;
	print "writen to: $file\n";
    }
}

sub recursive($$)
{
    my $dir = shift;
    $dir = "." if not defined $dir;
    
    $fileFilter = shift;
    $fileFilter = "/.*/" if not defined $fileFilter;
    
    my @dirs;
    push @dirs, $dir;
    find(\&wanted, @dirs );
    exit;
}

sub wanted()
{
    if (-e and not -d and eval $fileFilter)
    {
	print "$File::Find::name\n";
	$file = $_;
	$change = 0;
	&write(&read);
    }
}

sub usage()
{
    print "${red}Usage$norm:\tsubstitute.pl <y/n> </regex/substitution/> <file OR folder> [file filter regex]\n".
	      "\t\tsupstitutes either recursively or just a list of files\n";
    exit;
}





sub Color(;$$)
{
    my ($type, $color) = @_;
    return "[0m" if (not defined $type or not defined $color or $type eq 'none');
#    return "[$type;$Colors{$color}mTypeTest[0m" if ( not defined $ColorTypes{$type}   );
#    return "[$ColorTypes{$type};${color}mColorTest[0m" if ( not defined $Colors{$color} );
    die "ERROR: type  '$type'  not defined\n" if ( not defined $ColorTypes{$type}   );
    die "ERROR: color '$color' not defined\n" if ( not defined $Colors{$color} );
    return "[$ColorTypes{$type};$Colors{$color}m";
}
