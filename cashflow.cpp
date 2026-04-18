
#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 3) { cout << "{\"status\":\"error\",\"msg\":\"missing args\"}"; return 1; }
    ifstream in(argv[1]);
    if (!in) { cout << "{\"status\":\"error\",\"msg\":\"file not found\"}"; return 1; }

    map<string,double> client_cf; // cashflow netto per cliente
    map<string,double> cr,cc,ch,ce;
    double tr=0,tc=0,th=0,te=0;
    vector<double> cfv;
    bool extended=false;
    string line;

    while(getline(in,line)){
        if(line.empty()) continue;
        for(auto& c:line) if(c==';') c=',';
        stringstream ss(line);
        string a,b,c,d,e,f,g;
        getline(ss,a,','); getline(ss,b,','); getline(ss,c,',');
        getline(ss,d,','); getline(ss,e,','); getline(ss,f,','); getline(ss,g,',');
        if(a.empty()||b.empty()||c.empty()) continue;
        auto trim=[](string s){
            size_t x=s.find_first_not_of(" \t\r\n"),y=s.find_last_not_of(" \t\r\n");
            return x==string::npos?"":s.substr(x,y-x+1);
        };
        b=trim(b); c=trim(c); d=trim(d); e=trim(e); f=trim(f); g=trim(g);
        double rev=0;
        try{ rev=stod(c); }catch(...){continue;}

        double hrs_test=0,ch_test=0; try{hrs_test=stod(d);}catch(...){} try{ch_test=stod(e);}catch(...){} if(!d.empty()&&!e.empty()&&hrs_test>0&&ch_test>0){
            // Formato impiantisti
            double hrs=0,ch2=0,mat=0,est=0;
            try{hrs=stod(d);}catch(...){}
            try{ch2=stod(e);}catch(...){}
            try{if(!f.empty())mat=stod(f);}catch(...){}
            try{if(!g.empty())est=stod(g);}catch(...){}
            double cost=hrs*ch2+mat;
            double profit=rev-cost;
            cr[b]+=rev; cc[b]+=cost; ch[b]+=hrs; ce[b]+=est;
            tr+=rev; tc+=cost; th+=hrs; te+=est;
            client_cf[b]+=profit;
            cfv.push_back(profit);
            extended=true;
        } else {
            // Formato base: cashflow diretto
            client_cf[b]+=rev;
            cfv.push_back(rev);
            if(rev>0){cr[b]+=rev; tr+=rev;}
            else{cc[b]+=-rev; tc+=-rev;}
        }
    }

    if(cfv.empty()){cout<<"{\"status\":\"error\",\"msg\":\"empty dataset\"}";return 1;}

    // KPI 1: margine per cliente = cashflow netto
    string wc="",bc=""; double wm=0,bm=-1e18;
    for(auto& x:client_cf){
        if(x.second<wm){wm=x.second;wc=x.first;}
        if(x.second>bm){bm=x.second;bc=x.first;}
    }
    double tm=0; for(auto& x:client_cf) tm+=x.second;

    // KPI 2: ore non fatturate (solo formato impiantisti)
    double avail_h=th*1.2;
    double unbilled_h=(avail_h>0)?avail_h-th:0;
    double hrly=(th>0&&tr>0)?tr/th:0;
    double unbilled_val=unbilled_h*hrly;

    // KPI 3: scostamento
    double variance=(te>0)?tc-te:0;
    double var_pct=(te>0)?(variance/te)*100:0;

    // KPI 4: saturazione
    double saturation=(avail_h>0)?(th/avail_h)*100:0;

    // KPI 5: dipendenza (su revenue positiva)
    double top_v=0;
    for(auto& x:cr) if(x.second>top_v) top_v=x.second;
    double dep=(tr>0)?(top_v/tr)*100:0;

    // KPI 6: volatilita cashflow
    double cf_mean=0; for(double v:cfv) cf_mean+=v; cf_mean/=cfv.size();
    double cf_var=0; for(double v:cfv) cf_var+=pow(v-cf_mean,2); cf_var/=cfv.size();
    double vol=sqrt(cf_var);

    // KPI 7: costo orario reale
    double cph=(th>0)?tc/th:0;

    // KPI 8: efficienza (revenue/costo totale)
    double eff=(tc>0)?tr/tc:0;

    // HHI: calcolato su cashflow assoluto per cliente
    double total_abs=0;
    for(auto& x:client_cf) total_abs+=abs(x.second);
    double hhi=0;
    if(total_abs>0){
        for(auto& x:client_cf){
            double s=abs(x.second)/total_abs;
            hhi+=s*s;
        }
    }
    if(hhi>1.0) hhi=1.0;

    // Failure probability
    auto cl=[](double x){return x<0?0.0:(x>1?1.0:x);};
    auto sg=[](double x){return 1.0/(1.0+exp(-x));};
    double lr=(total_abs>0)?abs(wm)/total_abs:0;
    double fp=cl(0.30*cl(lr)+0.25*cl(dep/100)+0.20*sg((vol-400)/200)+0.15*cl(hhi)+0.10*cl(var_pct/100));
    double risk=fp*100;

    string diag="STABLE",act="Sistema in equilibrio";
    if(risk>=70){diag="CRITICAL: systemic risk";act="Ristrutturazione immediata";}
    else if(risk>=40){diag="HIGH RISK: instability detected";act="Ridurre perdite e diversificare";}

    double lm=(wm<0)?abs(wm):0;
    double la=lm*12,l90=lm*3,rec=la*(1-fp);

    vector<pair<string,double>> sm(client_cf.begin(),client_cf.end());
    sort(sm.begin(),sm.end(),[](auto&a,auto&b){return a.second<b.second;});

    cout<<fixed;
    cout<<"{";
    cout<<"\"diagnosis\":\""<<diag<<"\",\"action\":\""<<act<<"\",";
    cout<<"\"risk_score\":"<<risk<<",\"failure_probability\":"<<fp<<",";
    cout<<"\"worst_client\":\""<<wc<<"\",\"worst_margin\":"<<wm<<",";
    cout<<"\"best_client\":\""<<bc<<"\",\"best_margin\":"<<bm<<",";
    cout<<"\"total_margin\":"<<tm<<",\"total_revenue\":"<<tr<<",\"total_cost\":"<<tc<<",";
    cout<<"\"unbilled_hours\":"<<unbilled_h<<",\"unbilled_value\":"<<unbilled_val<<",";
    cout<<"\"budget_variance\":"<<variance<<",\"budget_variance_pct\":"<<var_pct<<",";
    cout<<"\"saturation\":"<<saturation<<",\"dependency\":"<<dep<<",";
    cout<<"\"volatility\":"<<vol<<",\"cashflow_tension\":"<<cf_mean<<",";
    cout<<"\"cost_per_hour\":"<<cph<<",\"efficiency\":"<<eff<<",";
    cout<<"\"concentration\":"<<hhi<<",";
    cout<<"\"loss_monthly\":"<<lm<<",\"loss_annual\":"<<la<<",\"loss_90d\":"<<l90<<",";
    cout<<"\"recovery_potential\":"<<rec<<",";
    cout<<"\"critical_client\":\""<<wc<<"\",\"margin\":"<<wm<<",";
    cout<<"\"has_extended\":"<<(extended?"true":"false")<<",";
    cout<<"\"top_losses\":[";
    int n=min((int)sm.size(),3);
    for(int i=0;i<n;i++){
        if(i>0) cout<<",";
        cout<<"{\"client\":\""<<sm[i].first<<"\",\"margin\":"<<sm[i].second<<"}";
    }
    cout<<"]}";
    return 0;
}
