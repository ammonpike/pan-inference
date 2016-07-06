#!perl

use lib "$ENV{PANLEX_TOOLDIR}/lib";
use PanLex::Client;
binmode STDOUT, ':encoding(utf8)';

#Score a distance-1 translation as the ration of the tq
#to the sum of all tq returned as translations of
#the given word into the given language from source language.

#"confidence rating"

my ($word1, $lang1, $lang2) = @ARGV;

my $query = panlex_query('/ex',
    {
        uid => $lang2,
        trtt => $word1,
        truid => $lang1,
        include => ['trq'],
        sort => 'trq desc'
    });

my $totalTQ = 0;
my %results;


foreach my $word (@{$query->{result}})
{
    $results{$word->{tt}} = $word->{trq};
    $totalTQ += $word->{trq};
}

foreach my $word (keys %results)
{
    $results{$word} = $results{$word} / $totalTQ;
}

my @sorted = sort { $results{$b} <=> $results{$a} } keys %results;

foreach my $word (@sorted)
{
    print $word . ": " . $results{$word} . "\n\n";
}