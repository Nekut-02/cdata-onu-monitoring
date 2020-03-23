#!/usr/bin/perl
use CGI qw/:standard/;
use strict;
use warnings;
use DBI;
use utf8;
binmode(STDOUT,':utf8');
use POSIX;

my $cgi = new CGI; 
my $source = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbc = DBI->connect($source, $username, $password, {mysql_enable_utf8 => 1});
$dbc->do("set names utf8");

print $cgi->header(
    -charset=>'UTF-8'
);

print $cgi->start_html(
    -title=>'Cdata Control',
    -style=>{'src'=>'/cdata/style.css'}
);

print qq'<div class="block-round-content"><a href="index.cgi">Панель управления Cdata</a></div>';

my $sth;
my @olt_ip = split( /\&/, $ENV{'QUERY_STRING'});
olt($olt_ip[0]);

sub olt($) {
    my $x = shift;
    my $ip = unpack("N",pack("C4",split(/\./,$x)));
    $sth = $dbc->prepare("select number, sugnal, mac, address, serial from olt_$ip order by number;");
    $sth->execute;
    print "<h3 align=\"center\">$x</h3>";
    print qq'
    <table border="1"><th>Номер порта</th><th>MAC</th><th>Сигнал</th><th>Описание</th><tr></tr>';
    while (my $ref = $sth->fetchrow_hashref()) {
        my $query = $ENV{'QUERY_STRING'};        
        print "<tr onclick=\"document.location = 'onu.cgi?$query&$ref->{'number'}'\" >";
        my $port = $ref->{'number'};  
        for ($port){
            my ($v, $p) = (floor($_/256) % 256 - 10, $_ % 64);
            print  "<td><b>",$v,"/",$p,"</b><br><small>",$port,"</small></td>";
        }
        print "<td>", $ref->{'mac'},"</td>"; 
        my $signal = $ref->{'sugnal'};
        for ($signal){
            if ($_ >= -24.9 && $_ <= -8){
                print "<td><font color=\"green\">", $signal,"</font></td>"; 
            }
            elsif ($_ >= -26 && $_ <= -25){
                print "<td><font color=\"#ff8000\">", $signal,"</font></td>"; 
            }
            elsif ($_ >= -27 ){
                print "<td><font color=\"red\">", $signal,"</font></td>"; 
            }
        }
        print "<td><font color=\"blue\">", $ref->{'address'},"</font><br><small>",$ref->{'serial'},"</small></td>";
        print "</tr>"; 
    }
    print qq'</table>';
}

$sth->finish;    
$dbc->disconnect;
