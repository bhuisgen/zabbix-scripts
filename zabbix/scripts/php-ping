#!/usr/bin/perl

use LWP::UserAgent;

if ($#ARGV+1 != 1) {
   print("Usage: php-ping <URL>\n");

   exit;
}

my $url = $ARGV[0];

my $ua = LWP::UserAgent->new(timeout => 15);
my $response = $ua->request(HTTP::Request->new('GET', $url));

if ($response->is_success && ($response->content == "pong")) {
   print "1\n";
   exit 0;
}
else {
   print "0\n";
   exit 1;
}
