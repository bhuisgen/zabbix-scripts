#!/usr/bin/perl

use LWP::UserAgent;

if ($#ARGV+1 != 2) {
   print("Usage: php <ITEM> <URL>\n");

   exit;
}

my $item = $ARGV[0];
my $url = $ARGV[1];

my $ua = LWP::UserAgent->new(timeout => 15);
my $response = $ua->request(HTTP::Request->new('GET', $url));
if ($response->is_success) {
   foreach (split(/\n/, $response->content)) {
      if (/$item:\s+(.+)/) {
         print "$1\n";
         exit 0;
      }
   }
}

exit 1;
